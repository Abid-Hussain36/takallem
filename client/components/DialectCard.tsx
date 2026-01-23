import { DialectResponse } from "@/types/response_models/ResourceResponse";
import styles from "./DialectCard.module.css";

interface DialectCardProps {
  dialect: DialectResponse;
  onDialectClick: (dialect: DialectResponse) => void;
}

const DialectCard = ({ dialect, onDialectClick }: DialectCardProps) => {
  return (
    <div
      className={styles.card}
      onClick={() => onDialectClick(dialect)}
      style={{
        backgroundImage: `url(${dialect.image})`,
      }}
    >
      <div className={styles.content}>
        <h2 className={styles.title} style={{ color: dialect.text_color }}>
          {dialect.dialect}
        </h2>
      </div>
    </div>
  );
};

export default DialectCard;
