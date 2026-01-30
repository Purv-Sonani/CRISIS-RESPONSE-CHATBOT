import React from "react";

export default function Header() {
  return (
    <div className="header-container">
      {/* 1. RED ALERT BAR */}
      <div className="header-alert">
        <div className="alert-content">
          <span>⚠️</span>
          <span>If someone is in immediate danger, call emergency services</span>
        </div>
        <button className="header-call-btn">📞 112</button>
      </div>

      {/* 2. BLUE TITLE BAR */}
      <div className="header-title-bar">
        <div className="header-icon">🛡️</div>
        <div>
          <div className="header-main-text">Emergency Assistant</div>
          <div className="header-sub-text">Automated guidance system</div>
        </div>
      </div>
    </div>
  );
}