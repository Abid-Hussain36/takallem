"use client";

import { useState } from 'react';
import { ModuleResponse } from '@/types/response_models/ModuleResponse';
import SectionAccordion from './SectionAccordion';
import styles from './UnitAccordion.module.css';

interface UnitAccordionProps {
  unitNumber: number;
  unitTitle: string;
  sections: { [sectionTitle: string]: ModuleResponse[] };
  currentModule: number;
  onModuleClick: (module: ModuleResponse) => void;
}

const UnitAccordion = ({ unitNumber, unitTitle, sections, currentModule, onModuleClick }: UnitAccordionProps) => {
  const [isOpen, setIsOpen] = useState(false);

  const allModules = Object.values(sections).flat();
  const completedCount = allModules.filter(m => m.number < currentModule).length;
  const totalCount = allModules.length;

  return (
    <div className={styles.container}>
      <div 
        className={`${styles.header} ${isOpen ? styles.open : ''}`}
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className={styles.headerContent}>
          <svg 
            className={`${styles.chevron} ${isOpen ? styles.chevronOpen : ''}`}
            width="24" 
            height="24" 
            viewBox="0 0 20 20" 
            fill="currentColor"
          >
            <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
          </svg>
          <div className={styles.titleContainer}>
            <span className={styles.unitNumber}>Unit {unitNumber}</span>
            <span className={styles.unitTitle}>{unitTitle}</span>
          </div>
        </div>
        <span className={styles.badge}>
          {completedCount}/{totalCount}
        </span>
      </div>
      
      <div className={`${styles.content} ${isOpen ? styles.contentOpen : ''}`}>
        <div className={styles.sectionsList}>
          {Object.entries(sections).map(([sectionTitle, sectionModules]) => (
            <SectionAccordion
              key={sectionTitle}
              sectionTitle={sectionTitle}
              modules={sectionModules}
              currentModule={currentModule}
              onModuleClick={onModuleClick}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default UnitAccordion;
