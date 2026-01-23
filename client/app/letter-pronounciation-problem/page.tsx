import { useResource } from "@/context/ResourceContext"


const LetterPronounciationProblem = () => {
    const {resource, setResource} = useResource();

    return(
        <h1>Letter Pronounciation Problem</h1>
    );
}

export default LetterPronounciationProblem;
