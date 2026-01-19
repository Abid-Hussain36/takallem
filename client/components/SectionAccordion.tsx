"use client";

import { useState } from 'react';
import { ModuleResponse } from '@/types/response_models/ModuleResponse';
import ModuleItem from './ModuleItem';
import styles from './SectionAccordion.module.css';

interface SectionAccordionProps {
  sectionTitle: string;
  modules: ModuleResponse[];
  currentModule: number;
  onModuleClick: (module: ModuleResponse) => void;
}

const SectionAccordion = ({ sectionTitle, modules, currentModule, onModuleClick }: SectionAccordionProps) => {
  const [isOpen, setIsOpen] = useState(false);

  const completedCount = modules.filter(m => m.number < currentModule).length;
  const totalCount = modules.length;

  return (
    <div className={styles.container}>
      <div 
        className={`${styles.header} ${isOpen ? styles.open : ''}`}
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className={styles.headerContent}>
          <svg 
            className={`${styles.chevron} ${isOpen ? styles.chevronOpen : ''}`}
            width="20" 
            height="20" 
            viewBox="0 0 20 20" 
            fill="currentColor"
          >
            <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
          </svg>
          <span className={styles.title}>{sectionTitle}</span>
        </div>
        <span className={styles.badge}>
          {completedCount}/{totalCount}
        </span>
      </div>
      
      <div className={`${styles.content} ${isOpen ? styles.contentOpen : ''}`}>
        <div className={styles.modulesList}>
          {modules.map((module) => (
            <ModuleItem
              key={module.id}
              title={module.title}
              number={module.number}
              isCompleted={module.number < currentModule}
              onClick={() => onModuleClick(module)}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default SectionAccordion;
