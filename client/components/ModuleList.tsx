"use client";

import { ModuleResponse } from '@/types/response_models/ModuleResponse';
import UnitAccordion from './UnitAccordion';
import styles from './ModuleList.module.css';

interface ModuleListProps {
  modules: ModuleResponse[];
  currentModule: number;
  onModuleClick: (module: ModuleResponse) => void;
}

const ModuleList = ({ modules, currentModule, onModuleClick }: ModuleListProps) => {
  // Group modules by unit, then by section
  const organizedModules = modules.reduce((acc, module) => {
    const unitKey = module.unit;
    const sectionKey = module.section;

    if (!acc[unitKey]) {
      acc[unitKey] = {};
    }
    if (!acc[unitKey][sectionKey]) {
      acc[unitKey][sectionKey] = [];
    }

    acc[unitKey][sectionKey].push(module);
    return acc;
  }, {} as { [unit: string]: { [section: string]: ModuleResponse[] } });

  // Sort units and sections
  const sortedUnits = Object.keys(organizedModules).sort((a, b) => {
    const numA = parseInt(a.match(/\d+/)?.[0] || '0');
    const numB = parseInt(b.match(/\d+/)?.[0] || '0');
    return numA - numB;
  });

  return (
    <div className={styles.container}>
      {sortedUnits.map((unit, index) => {
        const unitNumber = index + 1;
        return (
          <UnitAccordion
            key={unit}
            unitNumber={unitNumber}
            unitTitle={unit}
            sections={organizedModules[unit]}
            currentModule={currentModule}
            onModuleClick={onModuleClick}
          />
        );
      })}
    </div>
  );
};

export default ModuleList;
