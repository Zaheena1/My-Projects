import customtkinter as ctk
import threading
import queue
import json
import joblib
import os
from tkinter import messagebox

from agentSystem import BehavioralRiskAgent, ANNAgent, CoordinatorAgent, LLMReporter


# Defaults
NUMERICAL_FEATURES = ["account_age_days", "avg_amount_user", "amount", "shipping_distance_km"]
feature_order = [
    "account_age_days",
    "avg_amount_user",
    "amount",
    "shipping_distance_km",
    "avs_match",
    "cvv_result",
    "three_ds_flag",
]
encoders = {}

# Attempt to load preprocessing metadata (optional)


# Initialize agents
behavior_agent = BehavioralRiskAgent()
ann_agent = ANNAgent()
reporter = LLMReporter()
coordinator = CoordinatorAgent(behavioral_agent=behavior_agent, ann_agent=ann_agent, reporter=reporter)

behavior_agent.start()
ann_agent.start()
coordinator.start()


# UI
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

app = ctk.CTk()
app.title("🛡 ANN Fraud Detection System")
app.state("zoomed")

# Header
header = ctk.CTkFrame(app, height=90, fg_color="#0f172a")
header.pack(fill="x")

ctk.CTkLabel(header, text="🧠 ANN-Based Fraud Detection System", font=("Segoe UI", 32, "bold"), text_color="#38bdf8").pack(pady=10)
ctk.CTkLabel(header, text="Artificial Neural Network • Intelligent Agents • LLM Reasoning", font=("Segoe UI", 14), text_color="#cbd5e1").pack()

# Main layout
main = ctk.CTkFrame(app, fg_color="transparent")
main.pack(fill="both", expand=True, padx=30, pady=30)

# LEFT — inputs
left = ctk.CTkScrollableFrame(main, width=480, fg_color="#020617", corner_radius=18)
left.pack(side="left", fill="y", padx=15)

ctk.CTkLabel(left, text="Transaction Details", font=("Segoe UI", 22, "bold"), text_color="#e5e7eb").pack(pady=20)

entries = {}

def add_label(text):
    ctk.CTkLabel(left, text=text, font=("Segoe UI", 13), text_color="#e5e7eb").pack(anchor="w", pady=(14, 4))

for feature in feature_order:
    add_label(feature.replace("_", " ").title())
    if feature in encoders:
        try:
            vals = list(encoders[feature].classes_)
        except Exception:
            vals = [""]
        cb = ctk.CTkComboBox(left, values=vals, width=420)
        cb.pack()
        entries[feature] = cb
    elif feature in ("avs_match", "cvv_result", "three_ds_flag"):
        # Use 0/1 values to match previous behavior
        cb = ctk.CTkComboBox(left, values=["0", "1"], width=420)
        cb.pack()
        entries[feature] = cb
    else:
        en = ctk.CTkEntry(left, width=420, placeholder_text="Enter value")
        en.pack()
        entries[feature] = en

ctk.CTkButton(left, text="🔍 Analyze Transaction", height=55, width=420, font=("Segoe UI", 18, "bold"), fg_color="#2563eb", hover_color="#1e40af", command=lambda: predict()).pack(pady=30)

# RIGHT — results
right = ctk.CTkFrame(main, fg_color="#020617", corner_radius=18)
right.pack(side="right", fill="both", expand=True, padx=15)

ctk.CTkLabel(right, text="Transaction Report", font=("Segoe UI", 22, "bold"), text_color="#e5e7eb").pack(pady=20)

decision_label = ctk.CTkLabel(right, text="Awaiting Analysis", font=("Segoe UI", 28, "bold"), text_color="#38bdf8")
decision_label.pack(pady=10)

ann_prob_label = ctk.CTkLabel(right, text="ANN Probability: N/A", font=("Segoe UI", 14), text_color="#94a3b8")
ann_prob_label.pack(pady=6)

result_box = ctk.CTkTextbox(right, font=("Consolas", 12), corner_radius=12, fg_color="#020617", text_color="#e5e7eb", height=360)
result_box.pack(padx=25, pady=10, fill="both", expand=True)
result_box.insert("end", "Run analysis to view transaction report.")
result_box.configure(state="disabled")

action_frame = ctk.CTkFrame(right, fg_color="transparent")
action_frame.pack(pady=20)

# -------------------------------
# Helper Functions
# -------------------------------
def clear_inputs():
    """Clear all input fields for new transaction"""
    for e in entries.values():
        if hasattr(e, "set"):
            e.set("")
        else:
            e.delete(0, "end")

def reset_ui():
    """Reset UI elements (results only, NOT inputs)"""
    # Clear action buttons
    for widget in action_frame.winfo_children():
        widget.pack_forget()
    
    # Reset labels
    decision_label.configure(text="Awaiting Analysis", text_color="#38bdf8")
    ann_prob_label.configure(text="ANN Probability: N/A")
    
    # Clear result box
    result_box.configure(state="normal")
    result_box.delete("1.0", "end")
    result_box.insert("end", "Run analysis to view transaction report.")
    result_box.configure(state="disabled")

def approve_action(msg):
    messagebox.showinfo("Approved", msg)
    clear_inputs()  # Clear for new transaction
    reset_ui()

def reject_action(msg):
    messagebox.showwarning("Rejected", msg)
    clear_inputs()  # Clear for new transaction
    reset_ui()

approve_btn = ctk.CTkButton(action_frame, text="✅ APPROVE TRANSACTION", fg_color="#22c55e", hover_color="#16a34a", font=("Segoe UI", 16, "bold"), command=lambda: approve_action("Transaction Approved Successfully"))
reject_btn = ctk.CTkButton(action_frame, text="❌ REJECT TRANSACTION", fg_color="#ef4444", hover_color="#b91c1c", font=("Segoe UI", 16, "bold"), command=lambda: reject_action("Transaction Rejected"))
review_approve_btn = ctk.CTkButton(action_frame, text="✅ APPROVE AFTER REVIEW", fg_color="#22c55e", hover_color="#16a34a", font=("Segoe UI", 16, "bold"), command=lambda: approve_action("Approved After Manual Review"))
review_reject_btn = ctk.CTkButton(action_frame, text="❌ REJECT AFTER REVIEW", fg_color="#ef4444", hover_color="#b91c1c", font=("Segoe UI", 16, "bold"), command=lambda: reject_action("Rejected After Manual Review"))


# -------------------------------
# Report Formatting Function
# -------------------------------
def format_analysis_report(fusion, llm_report, ann_prob):
    """Format a professional, well-structured analysis report"""
    
    # Extract data
    ml_decision = fusion.get("ml_decision", "UNKNOWN")
    behavior_decision = fusion.get("behavior_decision", "NORMAL")
    final_decision = fusion.get("final_decision", "UNKNOWN")
    behavior_reasons = fusion.get("behavior_reasons", [])
    recommendations = fusion.get("recommendations", [])
    
    # Format ANN probability
    try:
        prob_percent = float(ann_prob) * 100
        prob_display = f"{prob_percent:.1f}%"
    except:
        prob_display = "N/A"
    
    # Build report sections
    report_parts = []
    
    # ═══════════════════════════════════════════════════════════
    # SECTION 1: ANN MODEL PREDICTION
    # ═══════════════════════════════════════════════════════════
    report_parts.append("═" * 70)
    report_parts.append("🤖 ARTIFICIAL NEURAL NETWORK (ANN) ANALYSIS")
    report_parts.append("═" * 70)
    report_parts.append(f"Fraud Probability: {prob_display}")
    report_parts.append(f"ML Decision: {ml_decision}")
    report_parts.append("")
    
    # ═══════════════════════════════════════════════════════════
    # SECTION 2: BEHAVIORAL RISK ANALYSIS
    # ═══════════════════════════════════════════════════════════
    report_parts.append("═" * 70)
    report_parts.append("📊 BEHAVIORAL RISK AGENT ANALYSIS")
    report_parts.append("═" * 70)
    report_parts.append(f"Status: {behavior_decision}")
    report_parts.append("")
    
    if behavior_reasons:
        report_parts.append("Findings:")
        for reason in behavior_reasons:
            report_parts.append(f"  • {reason}")
    else:
        report_parts.append("Findings:")
        report_parts.append("  • No abnormal patterns detected")
    report_parts.append("")
    
    # ═══════════════════════════════════════════════════════════
    # SECTION 3: LLM EXPERT ANALYSIS
    # ═══════════════════════════════════════════════════════════
    report_parts.append("═" * 70)
    report_parts.append("🧠 AI EXPERT ANALYSIS (LLM)")
    report_parts.append("═" * 70)
    report_parts.append(llm_report.strip())
    report_parts.append("")
    
    # ═══════════════════════════════════════════════════════════
    # SECTION 4: FINAL DECISION (COORDINATOR FUSION)
    # ═══════════════════════════════════════════════════════════
    report_parts.append("═" * 70)
    report_parts.append("⚖️ FINAL DECISION (COORDINATOR AGENT)")
    report_parts.append("═" * 70)
    
    # Decision with emoji
    if final_decision == "FRAUD":
        report_parts.append(f"Result: 🚨 {final_decision}")
    elif final_decision == "SAFE":
        report_parts.append(f"Result: ✅ {final_decision}")
    else:
        report_parts.append(f"Result: ⚠️ {final_decision}")
    
    report_parts.append("")
    
    if recommendations:
        report_parts.append("Recommended Actions:")
        for rec in recommendations:
            report_parts.append(f"  → {rec}")
    
    report_parts.append("")
    report_parts.append("═" * 70)
    
    return "\n".join(report_parts)


# -------------------------------
# Prediction Function
# -------------------------------
def predict():
    def worker():
        try:
            raw_input = {f: (entries[f].get() if hasattr(entries[f], 'get') else '') for f in feature_order}
            # Coerce numeric fields
            for f in NUMERICAL_FEATURES:
                try:
                    raw_input[f] = float(raw_input.get(f, 0) or 0)
                except Exception:
                    raw_input[f] = 0.0

            # Convert 0/1 strings to ints for avs/cvv/3ds
            for flag in ("avs_match", "cvv_result", "three_ds_flag"):
                v = raw_input.get(flag, "1")
                try:
                    raw_input[flag] = int(str(v).strip())
                except Exception:
                    raw_input[flag] = 1

            # Send to coordinator
            q = queue.Queue()
            coordinator.send({"type": "process_transaction", "transaction": raw_input, "reply_to": q})
            out = q.get(timeout=30.0)

            fusion = out.get("fusion_result", {})
            report_text = out.get("report", "")
            ann_prob = out.get("ann_probability")

            def ui_update():
                reset_ui()
                
                # Show ANN probability
                if ann_prob is not None:
                    try:
                        ann_prob_label.configure(text=f"ANN Probability: {float(ann_prob):.2f}")
                    except Exception:
                        ann_prob_label.configure(text=f"ANN Probability: {ann_prob}")

                decision = fusion.get("final_decision", "UNKNOWN")
                if decision == "FRAUD":
                    decision_label.configure(text="🚨 FRAUD DETECTED", text_color="#ef4444")
                    reject_btn.pack()
                elif decision == "SAFE":
                    decision_label.configure(text="✅ SAFE TRANSACTION", text_color="#22c55e")
                    approve_btn.pack()
                else:
                    decision_label.configure(text="⚠️ REVIEW REQUIRED", text_color="#f59e0b")
                    review_approve_btn.pack(side="left", padx=10)
                    review_reject_btn.pack(side="left", padx=10)

                # ✨ NEW STRUCTURED REPORT
                report = format_analysis_report(fusion, report_text, ann_prob)
                
                result_box.configure(state="normal")
                result_box.delete("1.0", "end")
                result_box.insert("end", report)
                result_box.configure(state="disabled")

            app.after(0, ui_update)
        except queue.Empty:
            app.after(0, lambda: messagebox.showerror("Timeout", "Coordinator did not respond in time."))
        except Exception as e:
            app.after(0, lambda: messagebox.showerror("Error", str(e)))

    threading.Thread(target=worker, daemon=True).start()


def on_close():
    try:
        behavior_agent.stop()
    except Exception:
        pass
    try:
        ann_agent.stop()
    except Exception:
        pass
    try:
        coordinator.stop()
    except Exception:
        pass
    app.destroy()


app.protocol("WM_DELETE_WINDOW", on_close)
app.mainloop()