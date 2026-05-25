
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

@st.cache_data(show_spinner=False)
def load_and_process_data(file_path):
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()
    ref_df = df[df["OF"].isin(["Nominal", "Tol Inf", "Tol Sup"])].set_index("OF")
    parts_df = df[~df["OF"].isin(["Nominal", "Tol Inf", "Tol Sup"])]
    all_characteristics = [c for c in df.columns if c != "OF"]
    return ref_df, parts_df, all_characteristics

@st.cache_data(show_spinner=False)
def build_multi_part_analysis_fast(parts_block, t_inf, t_sup):
    """
    Returns:
      within: bool matrix
      severity_codes: int8 matrix
        0 = Good
        1 = Moderate
        2 = High
        3 = Critical
    """
    low = np.minimum(t_inf, t_sup).astype(np.float32)
    high = np.maximum(t_inf, t_sup).astype(np.float32)

    vals = parts_block.to_numpy(dtype=np.float32, copy=True)

    within = (vals >= low) & (vals <= high)

    tol_span = high - low
    tol_span_safe = np.where(tol_span == 0, np.nan, tol_span)

    dist_to_edge = np.minimum(vals - low, high - vals)
    risk = dist_to_edge / tol_span_safe

    # severity codes
    severity_codes = np.zeros(vals.shape, dtype=np.int8)   # Good
    severity_codes[risk < 0.15] = 1                        # Moderate
    severity_codes[risk < 0.05] = 2                        # High
    severity_codes[~within] = 3                            # Critical

    return within, severity_codes


@st.cache_data(show_spinner=False)
def prepare_multi_part_severity_table(parts_block, all_characteristics, severity_filter, severity_codes):
    """
    Builds:
      sev_df     -> dataframe with OF + ✅/❌ display
      style_df   -> dataframe of CSS strings (same shape)
      visible_points -> actual visible selected severity point count
    """
    all_characteristics = list(all_characteristics)

    # code mapping
    code_map = {
        "Good": 0,
        "Moderate": 1,
        "High": 2,
        "Critical": 3
    }

    n_rows, n_cols = severity_codes.shape

    # if severity_filter == "All":
    #     keep_cols_mask = np.ones(n_cols, dtype=bool)
    # else:
    #     target_code = code_map[severity_filter]
    #     keep_cols_mask = (severity_codes == target_code).any(axis=0)

    # display_cols = np.array(all_characteristics)[keep_cols_mask].tolist()

    # if len(display_cols) == 0:
    #     return None, None, 0
    display_cols = list(all_characteristics)

    if len(display_cols) == 0:
        return None, None, 0

    filtered_codes = severity_codes

    # filtered_codes = severity_codes[:, keep_cols_mask]

    if severity_filter == "All":
        display = np.where(filtered_codes == 3, "❌", "✅")
        visible_points = int(filtered_codes.size)
    else:
        target_code = code_map[severity_filter]
        display = np.full(filtered_codes.shape, "", dtype=object)
        mask = filtered_codes == target_code

        # Critical -> ❌, others -> ✅
        display[mask] = np.where(target_code == 3, "❌", "✅")
        visible_points = int(mask.sum())

    sev_df = pd.DataFrame(
        display,
        index=parts_block.index,
        columns=display_cols
    )
    sev_df.index.name = "OF"
    sev_df = sev_df.reset_index()


    css_lookup = np.array([
        "background-color: #dcfce7; font-weight:700; text-align:center;",  # Good
        "background-color: #fef9c3; font-weight:700; text-align:center;",  # Moderate
        "background-color: #fb923c; font-weight:700; text-align:center;",  # High
        "background-color: #fecaca; font-weight:700; text-align:center;",  # Critical
    ], dtype=object)

    style_css = css_lookup[filtered_codes]

    if severity_filter != "All":
        # blank out style for hidden cells
        target_code = code_map[severity_filter]
        mask = filtered_codes == target_code
        style_css = np.where(mask, style_css, "")

    style_df = pd.DataFrame(style_css, columns=display_cols)
    style_df.insert(0, "OF", "")

    return sev_df, style_df, visible_points


def show():
    if st.button("⬅ Back to Home"):
        st.session_state.page = "home"
        st.rerun()

    # st.html("""
    #     <div style="
    #         width: 100%;
    #         display: flex;
    #         justify-content: center;
    #         margin-top: 20px;
    #         margin-bottom: 30px;
    #     ">
    #         <div style="
    #             width: 82%;
    #             background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 45%, #1d4ed8 100%);
    #             border: 1px solid rgba(255,255,255,0.12);
    #             border-radius: 26px;
    #             padding: 42px 40px;
    #             text-align: center;
    #             box-shadow: 0 14px 34px rgba(15, 23, 42, 0.35);
    #             position: relative;
    #             overflow: hidden;
    #         ">
    #             <!-- decorative glow circles -->
    #             <div style="
    #                 position: absolute;
    #                 top: -40px;
    #                 right: -30px;
    #                 width: 170px;
    #                 height: 170px;
    #                 background: rgba(255,255,255,0.08);
    #                 border-radius: 50%;
    #             "></div>

    #             <div style="
    #                 position: absolute;
    #                 bottom: -55px;
    #                 left: -55px;
    #                 width: 190px;
    #                 height: 190px;
    #                 background: rgba(255,255,255,0.06);
    #                 border-radius: 50%;
    #             "></div>

    #             <div style="
    #                 position: absolute;
    #                 top: 18px;
    #                 left: 28px;
    #                 width: 120px;
    #                 height: 120px;
    #                 background: radial-gradient(circle, rgba(255,255,255,0.10) 0%, rgba(255,255,255,0) 70%);
    #                 border-radius: 50%;
    #             "></div>

    #                 <h1 style="
    #                     margin: 0;
    #                     font-size: 50px;
    #                     font-weight: 800;
    #                     color: #ffffff;
    #                     line-height: 1.15;
    #                     letter-spacing: 0.2px;
    #                 ">
    #                     ORION: AI Driven Daily Production Assistant
    #                 </h1>

    #                 <p style="
    #                     margin: 18px 0 0 0;
    #                     font-size: 18px;
    #                     color: #dbeafe;
    #                     line-height: 1.7;
    #                     max-width: 900px;
    #                     margin-left: auto;
    #                     margin-right: auto;
    #                 ">
    #                 A centralized quality view for monitoring part compliance, characteristic stability, and manufacturing consistency.
    #                 </p>
    #             </div>
    #         </div>
    #     </div>
    #     """)

    st.title("📊 Characteristics Analytics")
    if "char_idx" not in st.session_state:
        st.session_state.char_idx = 0

    if "part_idx" not in st.session_state:
        st.session_state.part_idx = 0

    if "prev_view" not in st.session_state:
        st.session_state.prev_view = None

    ref_df, parts_df, all_characteristics = load_and_process_data("files/PartsInfo.xlsx")
    all_parts = parts_df["OF"].tolist()[1:]
    selected_parts = []
    
    current_view = st.session_state.get("dashboard_radio", "All Characteristics")
    use_multi = (
        st.session_state.get("ui_tab") == "📈 Dashboard Analysis"
        and "dashboard_radio" in st.session_state
        and st.session_state.dashboard_radio == "Latest 20 Parts"
    )

    if use_multi:
        latest_20_default = all_parts[-20:]

        selected_parts = st.multiselect(
            "Select Parts",
            options=all_parts,
            default=latest_20_default,
            key="multi_part_select"
        )

        if len(selected_parts) == 0:
            st.error("⚠️ Please select at least 1 part.")

    elif  st.session_state.get("ui_tab") == "📋 Tabular Analysis Multi Part":
        selected_parts = st.multiselect(
                "Select Parts",
                options=all_parts,
                default=all_parts[-20:],
                key="tabular_multi_parts"
            )
        if not selected_parts:
            st.error("⚠️ Please select at least 1 part.")
            st.stop()

    else:
        selected_part = st.selectbox(
            "Select Part Number",
            all_parts,
            key="part_select"
        )

        selected_parts = [selected_part]

    
    ui_tab = st.segmented_control(
        "",
        options=["📈 Dashboard Analysis", "📋 Tabular Analysis Single Part" , "📋 Tabular Analysis Multi Part"],
        default="📈 Dashboard Analysis",
        key="ui_tab"
    )

    nominals_all = ref_df.loc["Nominal", all_characteristics].values
    t_sup_all = ref_df.loc["Tol Sup", all_characteristics].values
    t_inf_all = ref_df.loc["Tol Inf", all_characteristics].values

    allowed_high_all = t_sup_all - nominals_all
    allowed_low_all = t_inf_all - nominals_all

    high_b = np.maximum(allowed_high_all, allowed_low_all)
    low_b = np.minimum(allowed_high_all, allowed_low_all)

    total_count = len(all_characteristics)

    analysis_rows = []

    for sel_part in selected_parts:
        part_row = parts_df.loc[parts_df["OF"] == sel_part].iloc[0]
        actuals_all = part_row[all_characteristics].values
        actual_devs_all = actuals_all - nominals_all
        global_is_within = (
            (actual_devs_all >= low_b) &
            (actual_devs_all <= high_b)
        )

        total_pass = np.sum(global_is_within)

        total_fail = total_count - total_pass

        part_status = (
            "Conforming"
            if total_fail == 0
            else "Non-Conforming"
        )

        analysis_rows.append({
            "part": sel_part,
            "row": part_row,
            "actuals": actuals_all,
            "devs": actual_devs_all,
            "within": global_is_within,
            "pass": total_pass,
            "fail": total_fail,
            "status": part_status
        })

    # ---------------------------------------
    # DEFAULT PART FOR SINGLE MODE
    # ---------------------------------------
    
    default_analysis = analysis_rows[0]

    part_row = default_analysis["row"]
    actuals_all = default_analysis["actuals"]
    actual_devs_all = default_analysis["devs"]
    global_is_within = default_analysis["within"]
    total_pass = default_analysis["pass"]
    total_fail = default_analysis["fail"]

    # --- TAB 1: DASHBOARD ANALYSIS ---
    if ui_tab == "📈 Dashboard Analysis":
        st.session_state.active_tab = "tab1"
        st.session_state.tab2_reset = False
        left_nav, right_main = st.columns([1, 5])

        with left_nav:
            view_options = ["All Characteristics", "Top 10 Characteristics", "Conforming",
                "Non-Conforming", "Latest 20 Parts"]
            current_view = st.session_state.get("dashboard_radio", "All Characteristics")
            safe_index = view_options.index(current_view) if current_view in view_options else 0

            view_mode = st.radio(
                "Filter View",
                view_options,
                index=safe_index,
                key="dashboard_radio"
            )

        with right_main:
            selected_chars_filter = st.multiselect(
                "Select Characteristics (Min 10, Max 20)",
                options=all_characteristics, default=None, key="dashboard_multi"
            )
            if len(selected_chars_filter)>0:
                st.write(f"Selected {len(selected_chars_filter)} Characteristics")

            if view_mode == "Latest 20 Parts":    
                total_characteristics = len(all_characteristics) * len(selected_parts)
                total_pass_characteristics = sum(np.sum(r["within"]) for r in analysis_rows)
                total_fail_characteristics = total_characteristics - total_pass_characteristics

                st.markdown('<div style="margin-bottom: 20px;"></div>', unsafe_allow_html=True)
                # Overall Summary Card
                st.markdown(f"""
                    <div style="background:#f8f9fb; padding:15px; border-radius:10px; border: 1px solid #e6e9ef;">
                        <h3 style="margin:0; font-size:16px; color:#1f2937;">Overall Summary For Selected ({len(selected_parts)} Parts)</h3>
                        <div style="display:flex; justify-content:space-between; margin-top:10px; font-size:14px;">
                            <div><b>Total:</b> {total_characteristics}</div>
                            <div style="color:#16a34a;"><b>Passed:</b> {total_pass_characteristics}</div>
                            <div style="color:#dc2626;"><b>Failed:</b> {total_fail_characteristics}</div>
                        </div>
                    </div>
                    <div style="margin-bottom: 25px;"></div>
                """, unsafe_allow_html=True)
            else:
                st.markdown('<div style="margin-bottom: 20px;"></div>', unsafe_allow_html=True)
                # Overall Summary Card
                st.markdown(f"""
                    <div style="background:#f8f9fb; padding:15px; border-radius:10px; border: 1px solid #e6e9ef;">
                        <h3 style="margin:0; font-size:16px; color:#1f2937;">Overall Summary For Selected ({len(selected_parts)} Parts)</h3>
                        <div style="display:flex; justify-content:space-between; margin-top:10px; font-size:14px;">
                            <div><b>Total:</b> {total_count}</div>
                            <div style="color:#16a34a;"><b>Passed:</b> {total_pass}</div>
                            <div style="color:#dc2626;"><b>Failed:</b> {total_fail}</div>
                        </div>
                    </div>
                    <div style="margin-bottom: 25px;"></div>
                """, unsafe_allow_html=True)

            # DEFAULT SAFE VALUE
            filtered_analysis = analysis_rows

            if view_mode == "Latest 20 Parts":
                latest_filter = st.radio(
                    "Part Status Filter",
                    ["All", "Conforming", "Non-Conforming"],
                    horizontal=True,
                    key="latest_filter_radio"
                )
                
                if "prev_filter" not in st.session_state:
                    st.session_state.prev_filter = latest_filter

                if st.session_state.prev_filter != latest_filter:
                    st.session_state.char_idx = 0
                    st.session_state.prev_filter = latest_filter


                if latest_filter == "All":
                    filtered_analysis = analysis_rows
                    indices = np.arange(len(all_characteristics))

                elif latest_filter == "Conforming":
                    filtered_analysis = analysis_rows  # Keep ALL parts

                    # Get characteristics where majority (or at least current part) is conforming
                    within_matrix = np.array([r["within"] for r in analysis_rows])

                    # Show characteristics where at least 1 part is conforming
                    indices = np.where(np.all(within_matrix, axis=0))[0]

                elif latest_filter == "Non-Conforming":
                    filtered_analysis = analysis_rows

                    within_matrix = np.array([r["within"] for r in analysis_rows])

                    # Show characteristics where ANY part failed
                    indices = np.where(~np.all(within_matrix, axis=0))[0]

            elif view_mode == "All Characteristics":
                indices = np.arange(total_count)

            elif view_mode == "Top 10 Characteristics":
                indices = np.arange(min(10, total_count))

            elif view_mode == "Conforming":
                indices = np.where(global_is_within)[0]
                filtered_analysis = analysis_rows

            elif view_mode == "Non-Conforming":
                indices = np.where(~global_is_within)[0]
                filtered_analysis = analysis_rows


            paged_analysis = filtered_analysis
                                        

            if "prev_view" not in st.session_state:
                st.session_state.prev_view = view_mode

            if st.session_state.prev_view != view_mode:
                st.session_state.start_idx = 0 
                st.session_state.char_idx = 0
                st.session_state.prev_view = view_mode
                st.session_state.pop("part_select", None)


            base_list = [all_characteristics[i] for i in indices]
            if selected_chars_filter:
                if 10 <= len(selected_chars_filter) <= 20:
                    # ✅ Intersection of both filters
                    target_list = [c for c in base_list if c in selected_chars_filter]
                else:
                    st.warning("⚠️ Select 10 to 20 items.")
                    target_list = base_list
            else:
                target_list = base_list


            # Windowing
            window_size = 10 if view_mode == "Top 10 Characteristics" else 20
            if "start_idx" not in st.session_state: st.session_state.start_idx = 0
            char_slice = target_list[
                st.session_state.char_idx :
                st.session_state.char_idx + window_size
            ]

            disable_nav = view_mode == "Top 10 Characteristics"

            # Summary boxes
            s_nom = ref_df.loc["Nominal", char_slice].values
            # s_dev = part_row[char_slice].values - s_nom
            s_up = ref_df.loc["Tol Sup", char_slice].values - s_nom
            s_lo = ref_df.loc["Tol Inf", char_slice].values - s_nom
            # win_fail = np.sum(~((s_dev >= np.minimum(s_up, s_lo)) & (s_dev <= np.maximum(s_up, s_lo))))
            # win_pass = len(char_slice) - win_fail
            if view_mode == "Latest 20 Parts":
                all_dev = np.array([
                    r["row"][char_slice].values - s_nom
                    for r in paged_analysis
                ])

                upper = np.maximum(s_up, s_lo)
                lower = np.minimum(s_up, s_lo)

                within_all = (all_dev >= lower) & (all_dev <= upper)

                if latest_filter == "Conforming":
                    # ✅ ONLY PASSED
                    win_pass = np.sum(within_all)
                    win_fail = 0

                elif latest_filter == "Non-Conforming":
                    # ✅ ONLY FAILED
                    win_fail = np.sum(~within_all)
                    win_pass = 0

                else:
                    # ✅ ALL
                    win_pass = np.sum(within_all)
                    win_fail = np.sum(~within_all)

            else:
                # ✅ Single part (no change)
                s_dev = part_row[char_slice].values - s_nom
                upper = np.maximum(s_up, s_lo)
                lower = np.minimum(s_up, s_lo)

                within_single = (s_dev >= lower) & (s_dev <= upper)

                win_pass = np.sum(within_single)
                win_fail = len(char_slice) - win_pass


            st.markdown(f"""
                <div style="display:flex; gap:10px;">
                    <div style="flex:1; background:#eff6ff; padding:10px; border-radius:8px; text-align:center; border:1px solid #dbeafe;">
                        <span style="font-size:18px; font-weight:bold; color:#1e40af;">{len(char_slice) * len(paged_analysis)}
<small>Chars View</small></span>
                    </div>
                    <div style="flex:1; background:#f0fdf4; padding:10px; border-radius:8px; text-align:center; border:1px solid #dcfce7;">
                        <span style="font-size:18px; font-weight:bold; color:#166534;">{win_pass}
<small>Chars Passed</small></span>
                    </div>
                    <div style="flex:1; background:#fef2f2; padding:10px; border-radius:8px; text-align:center; border:1px solid #fee2e2;">
                        <span style="font-size:18px; font-weight:bold; color:#dc2626;">{win_fail}
<small>Chars Failed</small></span>
                    </div>
                </div>
                <div style="margin-bottom: 20px;"></div>
            """, unsafe_allow_html=True)

            # Nav
            n1, n2, n3 = st.columns([0.1, 0.8, 0.1])
            with n1:
                if st.button("←", key="char_prev", disabled=disable_nav or st.session_state.char_idx == 0):
                    st.session_state.char_idx -= window_size
                    st.rerun()

            with n3:        
                if st.button("→", key="char_next",
                    disabled=disable_nav or (st.session_state.char_idx + window_size) >= len(target_list)):
                    st.session_state.char_idx += window_size
                    st.rerun()

            if len(char_slice) > 0:
                fig = go.Figure()
                # Tolerance zone
                fig.add_trace(
                    go.Scatter(
                        x=char_slice + char_slice[::-1],
                        y=list(s_up) + list(s_lo[::-1]),
                        fill='toself',
                        fillcolor='rgba(34, 197, 94, 0.05)',
                        line=dict(color='rgba(0,0,0,0)'),
                        showlegend=False,
                        name="Tolerance Zone"
                    )
                )

                # Upper tolerance
                fig.add_trace(
                    go.Scatter(
                        x=char_slice,
                        y=s_up,
                        name="Upper Tol",
                        line=dict(color="#16a34a", dash="dash")
                    )
                )

                # Lower tolerance
                fig.add_trace(
                    go.Scatter(
                        x=char_slice,
                        y=s_lo,
                        name="Lower Tol",
                        line=dict(color="#dc2626", dash="dash")
                    )
                )

                # ---------------------------------------------------------
                # SINGLE PART MODE
                # ---------------------------------------------------------

                if view_mode != "Latest 20 Parts":

                    recommendations = []

                    for i, c in enumerate(char_slice):

                        dev_val = s_dev[i]
                        upper = max(s_up[i], s_lo[i])
                        lower = min(s_up[i], s_lo[i])

                        if dev_val > upper:
                            issue = "Above upper tolerance"
                            reco = "Check machine offset & tooling alignment"

                        elif dev_val < lower:
                            issue = "Below lower tolerance"
                            reco = "Inspect fixture positioning & recalibrate"

                        else:
                            issue = "Within tolerance"
                            reco = "No action required"

                        recommendations.append(
                            f"""
                            <b>{c}</b><br>
                            Issue: {issue}<br>
                            Recommendation: {reco}
                            """
                        )

                    fig.add_trace(
                        go.Scatter(
                            x=char_slice,
                            y=s_dev,
                            name=f"{selected_part}",
                            mode="lines+markers",
                            line=dict(color="#7c3aed", width=3),
                            marker=dict(
                                size=10,
                                color=[
                                    "#dc2626"
                                    if not global_is_within[all_characteristics.index(c)]
                                    else "#16a34a"
                                    for c in char_slice
                                ]
                            ),
                            hovertemplate="%{customdata}<extra></extra>",
                            customdata=recommendations
                        )
                    )

                # ---------------------------------------------------------
                # LATEST 20 PARTS MODE
                # ---------------------------------------------------------

                else:

                    colors = [
                        "#7c3aed", "#2563eb", "#16a34a", "#dc2626",
                        "#ea580c", "#0891b2", "#9333ea", "#be123c",
                        "#0f766e", "#4f46e5"
                    ]

                    for idx, analysis in enumerate(paged_analysis):

                        part_row_multi = analysis["row"]

                        nom_slice = ref_df.loc["Nominal", char_slice].values
                        sup_slice = ref_df.loc["Tol Sup", char_slice].values
                        inf_slice = ref_df.loc["Tol Inf", char_slice].values

                        s_dev_multi = part_row_multi[char_slice].values - nom_slice

                        upper = np.maximum(sup_slice - nom_slice, inf_slice - nom_slice)
                        lower = np.minimum(sup_slice - nom_slice, inf_slice - nom_slice)

                        within_multi_slice = (s_dev_multi >= lower) & (s_dev_multi <= upper)
    

                        within_multi = analysis["within"]
                        if latest_filter == "Conforming":
                            y = [
                                s_dev_multi[i] if (s_dev_multi[i] >= lower[i] and s_dev_multi[i] <= upper[i]) else None
                                for i in range(len(char_slice))
                            ]

                        elif latest_filter == "Non-Conforming":
                            y = [
                                s_dev_multi[i] if (s_dev_multi[i] < lower[i] or s_dev_multi[i] > upper[i]) else None
                                for i in range(len(char_slice))
                            ]

                        else:
                            y = s_dev_multi

                        if latest_filter == "Conforming":
                            color = ["#16a34a" for _ in char_slice]

                        elif latest_filter == "Non-Conforming":
                            color = ["#dc2626" for _ in char_slice]

                        else:
                            color = [
                                "#16a34a" if (s_dev_multi[i] >= lower[i] and s_dev_multi[i] <= upper[i])
                                else "#dc2626"
                                for i in range(len(char_slice))
                            ]

                        fig.add_trace(
                            go.Scatter(
                                x=char_slice,
                                y=y,
                                mode="lines+markers",
                                name=str(analysis["part"]),
                                line=dict(
                                    color=colors[idx % len(colors)],
                                    width=2
                                ),
                                marker=dict(
                                    size=8,  
                                    color = color                                 
                                #     color=[
                                #     "#16a34a" if (s_dev_multi[i] >= lower[i] and s_dev_multi[i] <= upper[i]) else "#dc2626"
                                #     for i in range(len(char_slice))
                                # ]
                                ),
                                hovertemplate=(
                                    "<b>Part:</b> %{fullData.name}<br>"
                                    "<b>Characteristic:</b> %{x}<br>"
                                    "<b>Deviation:</b> %{y:.4f}<extra></extra>"
                                )
                            )
                        )

                # ---------------------------------------------------------
                # FINAL LAYOUT
                # ---------------------------------------------------------

                fig.update_layout(
                    title=dict(
                        text=(
                            "Latest 20 Parts Characteristics Analysis"
                            if view_mode == "Latest 20 Parts"
                            else f"Part Characteristics Analysis: {selected_part}"
                        ),
                        x=0.5,
                        xanchor="center",
                        font=dict(size=20)
                    ),
                    template="plotly_white",
                    height=600,
                    margin=dict(t=100),
                    legend=dict(
                        orientation="h",
                        y=1.12,
                        x=0.5,
                        xanchor="center"
                    )
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={"displayModeBar": False}
                )
                # ---------------------------------------------------------
                # NON-CONFORMING RECOMMENDATIONS
                # ---------------------------------------------------------

                st.markdown("---")

                st.subheader("⚠️ Non-Conforming Recommendations")

                # ---------------------------------------------------------
                # SINGLE PART MODE
                # ---------------------------------------------------------

                if view_mode != "Latest 20 Parts":

                    out_chars = []

                    for i, c in enumerate(char_slice):

                        dev_val = s_dev[i]

                        upper = max(s_up[i], s_lo[i])
                        lower = min(s_up[i], s_lo[i])

                        if dev_val < lower or dev_val > upper:

                            severity = (
                                "Critical" if abs(dev_val) >= 0.050
                                else "High" if abs(dev_val) >= 0.025
                                else "Moderate"
                            )

                            issue = (
                                "Above Upper Tolerance"
                                if dev_val > upper
                                else "Below Lower Tolerance"
                            )

                            recommendation = (
                                "Perform immediate machine recalibration and inspect tooling."
                                if severity == "Critical"
                                else "Inspect tool wear and verify fixture alignment."
                                if severity == "High"
                                else "Monitor process variation and verify setup."
                            )

                            out_chars.append({
                                "char": c,
                                "severity": severity,
                                "issue": issue,
                                "deviation": round(dev_val, 4),
                                "recommendation": recommendation
                            })

                    if len(out_chars) == 0:

                        st.success("✅ All displayed characteristics are within tolerance.")

                    else:

                        st.warning(
                            f"⚠️ {len(out_chars)} characteristic(s) require attention."
                        )

                        for item in out_chars:

                            if item["severity"] == "Critical":
                                border = "#dc2626"
                                bg = "#fef2f2"
                                icon = "🔴"

                            elif item["severity"] == "High":
                                border = "#ea580c"
                                bg = "#fff7ed"
                                icon = "🟠"

                            else:
                                border = "#ca8a04"
                                bg = "#fefce8"
                                icon = "🟡"

                            st.markdown(
                                f"""
                                <div style="
                                    border-left: 8px solid {border};
                                    background: {bg};
                                    padding: 18px;
                                    border-radius: 12px;
                                    margin-bottom: 14px;
                                    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
                                ">

                                <h4 style="margin-top:0;color:{border};">
                                    {icon} {item["char"]}
                                </h4>

                                <p><b>Severity:</b> {item["severity"]}</p>
                                <p><b>Issue:</b> {item["issue"]}</p>
                                <p><b>Deviation:</b> {item["deviation"]}</p>
                                <p><b>Recommendation:</b> {item["recommendation"]}</p>

                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                # ---------------------------------------------------------
                # LATEST 20 PARTS MODE
                # ---------------------------------------------------------

                else:                   
                    total_issues = 0

                    for analysis in paged_analysis:

                        part_name = analysis["part"]
                        part_row_multi = analysis["row"]

                        nom_slice = ref_df.loc["Nominal", char_slice].values
                        sup_slice = ref_df.loc["Tol Sup", char_slice].values
                        inf_slice = ref_df.loc["Tol Inf", char_slice].values

                        s_dev_multi = part_row_multi[char_slice].values - nom_slice

                        part_issues = []

                        for i, c in enumerate(char_slice):

                            dev_val = s_dev_multi[i]

                            upper_val = max(sup_slice[i] - nom_slice[i], inf_slice[i] - nom_slice[i])
                            lower_val = min(sup_slice[i] - nom_slice[i], inf_slice[i] - nom_slice[i])

                            if dev_val < lower_val or dev_val > upper_val:

                                severity = (
                                    "Critical" if abs(dev_val) >= 0.050
                                    else "High" if abs(dev_val) >= 0.025
                                    else "Moderate"
                                )

                                issue = (
                                    "Above Upper Tolerance"
                                    if dev_val > upper_val
                                    else "Below Lower Tolerance"
                                )

                                recommendation = (
                                    "Perform immediate machine recalibration and inspect tooling."
                                    if severity == "Critical"
                                    else "Inspect tool wear and verify fixture alignment."
                                    if severity == "High"
                                    else "Monitor process variation and verify setup."
                                )

                                part_issues.append({
                                    "char": c,
                                    "severity": severity,
                                    "issue": issue,
                                    "deviation": round(dev_val, 4),
                                    "recommendation": recommendation
                                })

                        if len(part_issues) > 0:

                            total_issues += len(part_issues)

                            st.markdown(f"## 🔧 Part: `{part_name}`")

                            for item in part_issues:

                                if item["severity"] == "Critical":
                                    border = "#dc2626"
                                    bg = "#fef2f2"
                                    icon = "🔴"

                                elif item["severity"] == "High":
                                    border = "#ea580c"
                                    bg = "#fff7ed"
                                    icon = "🟠"

                                else:
                                    border = "#ca8a04"
                                    bg = "#fefce8"
                                    icon = "🟡"

                                st.markdown(
                                    f"""
                                    <div style="
                                        border-left: 8px solid {border};
                                        background: {bg};
                                        padding: 18px;
                                        border-radius: 12px;
                                        margin-bottom: 14px;
                                        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
                                    ">

                                    <h4 style="margin-top:0;color:{border};">
                                        {icon} {item["char"]}
                                    </h4>

                                    <p><b>Severity:</b> {item["severity"]}</p>
                                    <p><b>Issue:</b> {item["issue"]}</p>
                                    <p><b>Deviation:</b> {item["deviation"]}</p>
                                    <p><b>Recommendation:</b> {item["recommendation"]}</p>

                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )

                    if total_issues == 0:

                        st.success(
                            "✅ All displayed parts are fully conforming."
                        )

    # --- TAB 2: TABULAR ANALYSIS ---
    elif ui_tab == '📋 Tabular Analysis Single Part':
        st.session_state.active_tab = "tab2"
        # Metrics at the top of the tab
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Items", total_count)
        m2.metric("Conforming", total_pass, delta=f"{total_pass/total_count:.1%}")
        m3.metric("Non-Conforming", total_fail, delta=f"-{(total_fail/total_count)*100:.1f}%")
        st.markdown('<div style="margin-bottom: 20px;"></div>', unsafe_allow_html=True)
        
        severity = st.radio("Severity Status", ["All", "Good", "Moderate", "High", "Critical"],horizontal=True)
        
        st.markdown('<div style="margin-bottom: 20px;"></div>', unsafe_allow_html=True)

        table_data = pd.DataFrame({
            "Characteristics": all_characteristics,
            "Nominal": nominals_all,
            "Actual": actuals_all,
            "Tol Lower": t_inf_all,
            "Tol Upper": t_sup_all,
            "Allowed Dev Lower": allowed_low_all,
            "Allowed Dev Upper": allowed_high_all,
            "Deviation": actual_devs_all,
            "Conforming": [
                "✅ Yes" if x else "❌ No"
                for x in global_is_within
            ]
        })   
        
        def compute_severity(actual, nominal, lower, upper):
            if pd.isnull(actual) or pd.isnull(nominal) or pd.isnull(lower) or pd.isnull(upper):
                return "Critical"

            low = min(lower, upper)
            high = max(lower, upper)

            if actual < low or actual > high:
                return "Critical"

            tol_span = high - low
            if tol_span == 0:
                return "Critical"

            dist_to_edge = min(actual - low, high - actual)

            risk = dist_to_edge / tol_span

            if risk < 0.05:
                return 'High'
            elif 0.05 <= risk < 0.15:
                return 'Moderate'
            elif risk >= 0.15:
                return 'Good'
            else:
                return 'Critical'

        
        severity_list = [
            compute_severity(actuals_all[i],nominals_all[i], t_inf_all[i], t_sup_all[i])
            for i in range(len(all_characteristics))
        ]

        table_data["Severity"] = severity_list

        if severity != "All":
            table_data = table_data[
                table_data["Severity"] == severity
            ]

        display_cols = [
            "Characteristics",
            "Nominal",
            "Actual",
            "Tol Lower",
            "Tol Upper",
            "Deviation",
            "Conforming",
            "Severity"
        ]


        st.dataframe(table_data[display_cols], use_container_width=True, hide_index=True,height=500)

        st.markdown("""
        ---
        ### Table Interpreation

        - **Deviation** → Difference between Actual and Nominal value.
        - **Conforming**
        - ✅ Yes = Within tolerance
        - ❌ No = Outside tolerance

        ### Severity Logic

        Severity is based on how close the measured value is to the tolerance limits.

        To calculate this, a **Risk Margin** is used:

        Risk Margin = Distance to nearest tolerance limit ÷ Total tolerance range

        This helps identify measurements that are still conforming but are dangerously close to failing.

        - **Critical** → Outside tolerance
        - **High** → Very close to tolerance limit (<5% margin remaining)
        - **Moderate** → Near tolerance limit (5%–15% margin)
        - **Good** → Safely within tolerance
        """)

    else:
        st.subheader("📋 Multi Part Tabular Analysis")
        
        total_characteristics = len(all_characteristics) * len(selected_parts)
        total_pass_characteristics = sum(np.sum(r["within"]) for r in analysis_rows)
        total_fail_characteristics = total_characteristics - total_pass_characteristics

        COL_WINDOW = 40
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Items", total_characteristics)
        m2.metric(
            "Conforming",
            total_pass_characteristics,
            delta=f"{(total_pass_characteristics / total_characteristics):.1%}" if total_characteristics else "0%"
        )
        m3.metric(
            "Non-Conforming",
            total_fail_characteristics,
            delta=f"-{(total_fail_characteristics / total_characteristics) * 100:.1f}%" if total_characteristics else "0%"
        )

        st.markdown('<div style="margin-bottom: 20px;"></div>', unsafe_allow_html=True)
        
        if "col_start" not in st.session_state:
            st.session_state.col_start = 0

        selected_chars_filter = st.multiselect(
                "Select Characteristics (Min 10, Max 20)",
                options=all_characteristics, default=None, key="dashboard_multi"
            )
        if len(selected_chars_filter)>0:
            st.write(f"Selected {len(selected_chars_filter)} Characteristics")

        filtered_characteristics = (
            selected_chars_filter
            if selected_chars_filter
            else all_characteristics
        )

        is_filtered = bool(selected_chars_filter)

        severity_filter = st.radio(
            "Severity Status",
            ["All", "Good", "Moderate", "High", "Critical"],
            horizontal=True,
            key="multi_tabular_severity"
        )

        st.markdown('<div style="margin-bottom: 15px;"></div>', unsafe_allow_html=True)

        parts_block = (
            parts_df[parts_df["OF"].isin(selected_parts)]
            .set_index("OF")[filtered_characteristics]
        )

        t_inf = ref_df.loc["Tol Inf", filtered_characteristics].to_numpy(dtype=np.float32)
        t_sup = ref_df.loc["Tol Sup", filtered_characteristics].to_numpy(dtype=np.float32)

        
        title_placeholder = st.empty()
        caption_placeholder = st.empty()
        table_placeholder = st.empty()

        within, severity_codes = build_multi_part_analysis_fast(
            parts_block,
            t_inf,
            t_sup
        )

        sev_df, style_df, visible_points = prepare_multi_part_severity_table(
            parts_block,
            tuple(filtered_characteristics),
            severity_filter,
            severity_codes
        )

        if severity_filter != "All":

            # Keep only non-blank columns
            non_blank_cols = ["OF"] + [
                col for col in sev_df.columns
                if col != "OF" and (sev_df[col] != "").any()
            ]

            sev_df = sev_df[non_blank_cols]
            style_df = style_df[non_blank_cols]

            # Keep only rows having visible values
            row_mask = (sev_df.drop(columns=["OF"]) != "").any(axis=1)

            sev_df = sev_df[row_mask].reset_index(drop=True)
            style_df = style_df[row_mask].reset_index(drop=True)


        available_cols = [
            c for c in sev_df.columns
            if c != "OF"
        ]

        # safety reset
        if st.session_state.col_start >= len(available_cols):
            st.session_state.col_start = 0

        if is_filtered:
            visible_cols = available_cols

        else:
            visible_cols = available_cols[
                st.session_state.col_start:
                st.session_state.col_start + COL_WINDOW
            ]

        if severity_filter != "All":

            non_blank_cols = ["OF"] + [
                col for col in sev_df.columns
                if col != "OF" and (sev_df[col] != "").any()
            ]

            sev_df = sev_df[non_blank_cols]
            style_df = style_df[non_blank_cols]

            row_mask = (sev_df.drop(columns=["OF"]) != "").any(axis=1)

            sev_df = sev_df[row_mask].reset_index(drop=True)
            style_df = style_df[row_mask].reset_index(drop=True)

        if sev_df is None:
            st.warning(f"⚠️ No characteristics found with severity '{severity_filter}'.")
            st.stop()

        def style_severity_only(_):
            return style_df
        
        fixed_cols = ["OF"]

        valid_cols = [c for c in visible_cols if c in sev_df.columns]

        visible_df = sev_df[fixed_cols + valid_cols]

        if not is_filtered:
            c1, c2, c3 = st.columns([1,10,1])

            with c1:
                if st.button("⬅ Prev 40"):
                    st.session_state.col_start = max(
                        0,
                        st.session_state.col_start - COL_WINDOW
                    )
                    st.rerun()

            with c2:
                st.markdown(
                    f"""
                    <div style='text-align:center;padding-top:8px'>
                   Showing columns
                        <b>{st.session_state.col_start + 1}</b>
                        -
                        <b>{
                            min(
                                st.session_state.col_start + COL_WINDOW,
                                len(available_cols)
                            )
                        }</b>
                        of <b>{len(available_cols)}</b>
                    """,
                    unsafe_allow_html=True
                )

            with c3:
                if st.button("Next 40 ➡"):
                    if st.session_state.col_start + COL_WINDOW < len(available_cols):
                        st.session_state.col_start += COL_WINDOW
                        st.rerun()

        title_placeholder.markdown("### 🎯 Severity Table")
        caption_placeholder.caption(f"Visible severity points: {visible_points}")

        valid_cols = [c for c in visible_cols if c in style_df.columns]

        table_placeholder.dataframe(
            visible_df.style.apply(
                lambda _: style_df.reindex(columns=valid_cols, fill_value=""),
                axis=None
            ),
            use_container_width=True,
            hide_index=True,
            height=550
        )


        st.markdown("""
        ---
        ### Legend

        - ✅ **Conforming / Right** → Value is within tolerance
        - ❌ **Non-Conforming / Wrong** → Value is outside tolerance

        ### Severity Color Coding
        - <span style="background-color:#dcfce7; padding:4px 10px; border-radius:6px;"><b>Good</b></span> → Safely within tolerance
        - <span style="background-color:#fef9c3; padding:4px 10px; border-radius:6px;"><b>Moderate</b></span> → Near tolerance limit
        - <span style="background-color:#fb923c; padding:4px 10px; border-radius:6px;"><b>High</b></span> → Very close to tolerance limit
        - <span style="background-color:#fecaca; padding:4px 10px; border-radius:6px;"><b>Critical</b></span> → Outside tolerance

        ### Severity Logic
        Risk Margin = Distance to nearest tolerance limit ÷ Total tolerance range

        - **Critical** → Outside tolerance
        - **High** → Very close to tolerance limit (< 5% remaining margin)
        - **Moderate** → Near tolerance limit (5%–15% margin)
        - **Good** → Safely within tolerance
        """, unsafe_allow_html=True)
