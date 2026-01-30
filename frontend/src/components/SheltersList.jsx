import React from "react";

const SheltersList = ({ data }) => {
  // Guard clause: If no data, render nothing to avoid crashes
  if (!data || data.length === 0) return null;

  return (
    <div className="shelter-container">
      {data.map((shelter, index) => (
        <div key={index} className="shelter-card">
          <div className="shelter-header">
            <div className="shelter-icon">📍</div>
            <div className="shelter-info">
              {/* Dynamic Name */}
              <h3>{shelter.name}</h3>
              
              <div className="shelter-meta">
                {/* Dynamic Distance */}
                <span>{shelter.distance}</span>
                {/* Static Badge */}
                <span className="badge available">Space available</span>
              </div>
              
              {/* Dynamic Address */}
              <p className="shelter-desc">{shelter.address}</p>
            </div>
          </div>
          
          {/* Dynamic Map Link */}
          <button 
            className="directions-btn"
            onClick={() => window.open(shelter.maps_link, "_blank")}
          >
            ➤ Get directions
          </button>
        </div>
      ))}
    </div>
  );
};

export default SheltersList;