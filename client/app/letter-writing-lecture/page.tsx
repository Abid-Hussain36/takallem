import { useResource } from "@/context/ResourceContext"


const LetterWritingLecture = () => {
    const {resource, setResource} = useResource();

    return(
        <h1>Letter Writing Lecture</h1>
    );
}

export default LetterWritingLecture;
