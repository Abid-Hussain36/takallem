import styles from './CourseProgress.module.css';

interface CourseProgressProps {
  courseName: string;
  currentModule: number;
  totalModules: number;
}

const CourseProgress = ({ courseName, currentModule, totalModules }: CourseProgressProps) => {
  const progressPercentage = Math.min((currentModule / totalModules) * 100, 100);

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>{courseName}</h1>
        <span className={styles.stats}>
          Module {currentModule} of {totalModules}
        </span>
      </div>
      <div className={styles.progressBarContainer}>
        <div 
          className={styles.progressBarFill}
          style={{ width: `${progressPercentage}%` }}
        >
          <span className={styles.progressText}>
            {Math.round(progressPercentage)}%
          </span>
        </div>
      </div>
    </div>
  );
};

export default CourseProgress;
