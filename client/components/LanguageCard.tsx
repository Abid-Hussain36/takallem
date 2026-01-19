import { LanguageResponse } from "@/types/response_models/LanguageResponse";
import { CourseResponse } from "@/types/response_models/CourseResponse";
import { useState } from "react";
import styles from "./LanguageCard.module.css";

interface LanguageCardProps {
  language: LanguageResponse;
  onLanguageSelect: (courses: CourseResponse[]) => void;
}

const LanguageCard = ({ language, onLanguageSelect }: LanguageCardProps) => {
  const [showAlert, setShowAlert] = useState(false);
  const hasCourses = language.courses && language.courses.length > 0;

  const handleClick = () => {
    if (hasCourses) {
      onLanguageSelect(language.courses);
    } else {
      setShowAlert(true);
      setTimeout(() => setShowAlert(false), 3000);
    }
  };

  return (
    <>
      <div
        className={`${styles.card} ${!hasCourses ? styles.disabled : ""}`}
        onClick={handleClick}
        style={{
          backgroundImage: `url(${language.image})`,
          cursor: hasCourses ? "pointer" : "not-allowed",
        }}
      >
        <div className={styles.content}>
          <h2 className={styles.title} style={{ color: language.text_color }}>
            {language.language}
          </h2>
        </div>
      </div>

      {showAlert && (
        <div className={styles.alertOverlay} onClick={() => setShowAlert(false)}>
          <div className={styles.alert} onClick={(e) => e.stopPropagation()}>
            <div className={styles.alertIcon}>🚧</div>
            <h3 className={styles.alertTitle}>Coming Soon!</h3>
            <p className={styles.alertMessage}>
              {language.language} courses are currently under development. Stay tuned!
            </p>
            <button className={styles.alertButton} onClick={() => setShowAlert(false)}>
              Got it
            </button>
          </div>
        </div>
      )}
    </>
  );
};

export default LanguageCard;