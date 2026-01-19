import styles from './ModuleItem.module.css';

interface ModuleItemProps {
  title: string;
  number: number;
  isCompleted: boolean;
  onClick: () => void;
}

const ModuleItem = ({ title, number, isCompleted, onClick }: ModuleItemProps) => {
  return (
    <div 
      className={`${styles.container} ${isCompleted ? styles.completed : ''}`}
      onClick={onClick}
    >
      <div className={styles.content}>
        <span className={styles.number}>{number}</span>
        <span className={styles.title}>{title}</span>
      </div>
      <div className={styles.indicator}>
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
        ) : (
          <div className={styles.circle} />
        )}
      </div>
    </div>
  );
};

export default ModuleItem;
