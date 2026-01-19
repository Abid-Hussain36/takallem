import { CourseResponse } from "@/types/response_models/CourseResponse";
import styles from "./CourseCard.module.css";

interface CourseCardProps {
  course: CourseResponse;
  onCourseClick: (course: CourseResponse) => void;
}

const CourseCard = ({ course, onCourseClick }: CourseCardProps) => {
  return (
    <div
      className={styles.card}
      onClick={() => onCourseClick(course)}
      style={{
        backgroundImage: `url(${course.image})`,
      }}
    >
      <div className={styles.content}>
        <h2 className={styles.title} style={{ color: course.text_color }}>
          {course.course_name}
        </h2>
      </div>
    </div>
  );
};

export default CourseCard;
