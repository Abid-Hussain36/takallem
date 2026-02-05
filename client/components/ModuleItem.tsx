import styles from './ModuleItem.module.css';

interface ModuleItemProps {
  title: string;
  number: number;
  currentModule: number;
  refModules: Set<number> | null;
  onClick: () => void;
}

const ModuleItem = ({ title, number, currentModule, refModules, onClick }: ModuleItemProps) => {
  // Determine module state
  const isCompleted = number < currentModule;
  const isCurrent = number === currentModule;
  const isReference = refModules?.has(number) || false;
  const isLocked = number > currentModule; // All modules greater than current are locked
  const isClickable = isCurrent || (isReference && number < currentModule); // Only current or past reference modules are clickable

  const handleClick = () => {
    if (isClickable) {
      onClick();
    }
  };

  return (
    <div 
      className={`
        ${styles.container} 
        ${isCompleted ? styles.completed : ''} 
        ${isLocked ? styles.locked : ''}
        ${!isClickable ? styles.disabled : ''}
      `}
      onClick={handleClick}
    >
      <div className={styles.content}>
        <span className={styles.number}>{number}</span>
        <span className={styles.title}>{title}</span>
      </div>
      <div className={styles.indicator}>
        {isReference && (
          <svg 
            className={styles.lectureIcon} 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            strokeWidth="2"
          >
            <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
            <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
          </svg>
        )}
        {isCompleted ? (
          <svg 
            className={styles.checkmark} 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="white" 
            strokeWidth="3"
          >
            <polyline points="20 6 9 17 4 12" />
          </svg>
        ) : isLocked ? (
          <svg 
            className={styles.lockIcon} 
            viewBox="0 0 24 24" 
            fill="currentColor"
          >
            <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zM9 8V6c0-1.66 1.34-3 3-3s3 1.34 3 3v2H9z"/>
          </svg>
        ) : (
          <div className={styles.circle} />
        )}
      </div>
    </div>
  );
};

export default ModuleItem;
