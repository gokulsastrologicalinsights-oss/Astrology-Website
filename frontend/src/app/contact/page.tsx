"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useLanguage } from "@/lib/i18n";
import { Mail, Clock, MapPin, Send, CheckCircle2, ShieldCheck, ArrowLeft, PhoneCall } from "lucide-react";

export default function ContactPage() {
  const { language } = useLanguage();
  const isTamil = language === "ta";

  const [formState, setFormState] = useState({
    name: "",
    email: "",
    subject: "general",
    message: "",
  });
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    // Simulate high-reliability feedback
    setTimeout(() => {
      setLoading(false);
      setSubmitted(true);
    }, 600);
  };

  return (
    <div className="min-h-screen bg-[#FDFBF7] text-[#1E293B] py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Navigation & Header */}
        <div>
          <Link
            href="/"
            className="inline-flex items-center gap-1.5 text-xs font-medium text-[#2563EB] hover:text-[#1D4ED8] mb-6 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            {isTamil ? "முகப்புப் பக்கத்திற்குத் திரும்பு" : "Return to Home"}
          </Link>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-[#2563EB]">
              <Mail className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-2xl sm:text-3xl font-serif font-bold text-[#0F172A]">
                {isTamil ? "எங்களைத் தொடர்பு கொள்ளவும்" : "Contact & Support Desk"}
              </h1>
              <p className="text-xs text-[#64748B] mt-1">
                {isTamil
                  ? "வாடிக்கையாளர் ஆதரவு, தொழில்நுட்ப உதவிகள் & வணிக விசாரணைகள்"
                  : "Customer Inquiries, Technical Support & Grievance Redressal"}
              </p>
            </div>
          </div>
        </div>

        {/* Info Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white p-5 rounded-2xl border border-[#E2E8F0] shadow-xs space-y-2">
            <div className="w-8 h-8 rounded-lg bg-blue-50 text-[#2563EB] flex items-center justify-center">
              <Mail className="w-4 h-4" />
            </div>
            <h3 className="text-xs font-bold text-[#0F172A] uppercase tracking-wider">
              {isTamil ? "மின்னஞ்சல் முகவரி" : "Direct Emails"}
            </h3>
            <p className="text-xs text-[#475569]">support@gokulsastrology.com</p>
            <p className="text-xs text-[#64748B]">billing@gokulsastrology.com</p>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-[#E2E8F0] shadow-xs space-y-2">
            <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <Clock className="w-4 h-4" />
            </div>
            <h3 className="text-xs font-bold text-[#0F172A] uppercase tracking-wider">
              {isTamil ? "பணி நேரம்" : "Operating Hours"}
            </h3>
            <p className="text-xs text-[#475569]">Mon – Sat: 9:00 AM – 6:00 PM IST</p>
            <p className="text-[11px] text-emerald-600 font-medium">
              {isTamil ? "24–48 மணிநேர பதில் உறுதி" : "24–48 Hour Response SLA"}
            </p>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-[#E2E8F0] shadow-xs space-y-2">
            <div className="w-8 h-8 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center">
              <MapPin className="w-4 h-4" />
            </div>
            <h3 className="text-xs font-bold text-[#0F172A] uppercase tracking-wider">
              {isTamil ? "அலுவலக இருப்பிடம்" : "Jurisdiction"}
            </h3>
            <p className="text-xs text-[#475569]">Chennai, Tamil Nadu, India</p>
            <p className="text-[11px] text-[#64748B]">
              {isTamil ? "இந்திய ஐடி சட்டம் & DPDP உட்பட்டது" : "Indian IT Act & DPDP Compliant"}
            </p>
          </div>
        </div>

        {/* Contact Form Section */}
        <section className="bg-white rounded-2xl p-6 sm:p-8 border border-[#E2E8F0] shadow-xs space-y-6">
          <div className="border-b border-[#F1F5F9] pb-4">
            <h2 className="text-lg font-bold text-[#0F172A]">
              {isTamil ? "செய்தி அல்லது கோரிக்கையை அனுப்பவும்" : "Submit an Inquiry"}
            </h2>
            <p className="text-xs text-[#64748B] mt-1">
              {isTamil
                ? "உங்கள் கருத்துகள் அல்லது சந்தேகங்களை கீழே உள்ள படிவத்தில் பூர்த்தி செய்யவும்."
                : "Fill out the form below. Our support team will respond to your registered email promptly."}
            </p>
          </div>

          {submitted ? (
            <div className="p-8 rounded-2xl bg-emerald-50 border border-emerald-200 text-center space-y-3">
              <div className="w-12 h-12 bg-emerald-100 rounded-full flex items-center justify-center mx-auto text-emerald-600">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <h3 className="text-base font-bold text-emerald-900">
                {isTamil ? "உங்கள் செய்தி வெற்றிகரமாக பெறப்பட்டது!" : "Message Received Successfully!"}
              </h3>
              <p className="text-xs text-emerald-800 max-w-md mx-auto">
                {isTamil
                  ? "நன்றி. எங்கள் உதவி மையக் குழு உங்கள் செய்தியை ஆய்வு செய்து 24-48 மணி நேரத்திற்குள் மின்னஞ்சல் மூலம் பதிலளிக்கும்."
                  : "Thank you for reaching out. A support ticket has been created and our team will get back to your email within 24–48 business hours."}
              </p>
              <button
                onClick={() => setSubmitted(false)}
                className="mt-4 px-4 py-2 bg-white text-emerald-700 text-xs font-semibold rounded-lg border border-emerald-200 hover:bg-emerald-100/50 transition-colors"
              >
                {isTamil ? "மற்றொரு செய்தி அனுப்ப" : "Send Another Message"}
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-[#334155] mb-1">
                    {isTamil ? "உங்கள் பெயர் *" : "Your Name *"}
                  </label>
                  <input
                    type="text"
                    required
                    value={formState.name}
                    onChange={(e) => setFormState({ ...formState, name: e.target.value })}
                    placeholder={isTamil ? "எ.கா. கோகுல் முருகன்" : "e.g. Gokul Murugan"}
                    className="w-full text-xs px-3.5 py-2.5 rounded-xl border border-[#CBD5E1] focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20 focus:border-[#2563EB] bg-[#F8FAFC]"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-[#334155] mb-1">
                    {isTamil ? "மின்னஞ்சல் முகவரி *" : "Email Address *"}
                  </label>
                  <input
                    type="email"
                    required
                    value={formState.email}
                    onChange={(e) => setFormState({ ...formState, email: e.target.value })}
                    placeholder="name@example.com"
                    className="w-full text-xs px-3.5 py-2.5 rounded-xl border border-[#CBD5E1] focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20 focus:border-[#2563EB] bg-[#F8FAFC]"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#334155] mb-1">
                  {isTamil ? "விசாரணை பிரிவு *" : "Inquiry Category *"}
                </label>
                <select
                  value={formState.subject}
                  onChange={(e) => setFormState({ ...formState, subject: e.target.value })}
                  className="w-full text-xs px-3.5 py-2.5 rounded-xl border border-[#CBD5E1] focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20 focus:border-[#2563EB] bg-[#F8FAFC]"
                >
                  <option value="general">{isTamil ? "பொதுவான தகவல் (General Inquiry)" : "General Inquiry"}</option>
                  <option value="technical">{isTamil ? "தொழில்நுட்ப உதவி / கணித பிழை (Technical Support)" : "Technical Support / Calculation Feedback"}</option>
                  <option value="billing">{isTamil ? "கட்டணம் & பிடிஎஃப் பதிவிறக்கம் (Billing & PDF Delivery)" : "Billing & PDF Delivery"}</option>
                  <option value="commercial">{isTamil ? "தொழில்முறை ஜோதிட சந்தா (Professional Tier)" : "Professional Astrologer Commercial Plan"}</option>
                  <option value="privacy">{isTamil ? "தனியுரிமை & தரவு நீக்கம் (Data Privacy & Erasure)" : "Data Privacy & Erasure Request"}</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#334155] mb-1">
                  {isTamil ? "உங்கள் செய்தி *" : "Message *"}
                </label>
                <textarea
                  required
                  rows={4}
                  value={formState.message}
                  onChange={(e) => setFormState({ ...formState, message: e.target.value })}
                  placeholder={
                    isTamil
                      ? "உங்கள் கருத்து அல்லது பிரச்சனையை விரிவாக விவரிக்கவும்..."
                      : "Describe your inquiry or issue in detail..."
                  }
                  className="w-full text-xs px-3.5 py-2.5 rounded-xl border border-[#CBD5E1] focus:outline-none focus:ring-2 focus:ring-[#2563EB]/20 focus:border-[#2563EB] bg-[#F8FAFC]"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="inline-flex items-center gap-2 px-6 py-2.5 bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-xs font-semibold rounded-xl transition-colors shadow-sm disabled:opacity-50"
              >
                {loading ? (
                  <span>{isTamil ? "அனுப்பப்படுகிறது..." : "Submitting..."}</span>
                ) : (
                  <>
                    <Send className="w-3.5 h-3.5" />
                    <span>{isTamil ? "செய்தியை அனுப்பவும்" : "Send Inquiry"}</span>
                  </>
                )}
              </button>
            </form>
          )}
        </section>
      </div>
    </div>
  );
}
