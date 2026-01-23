import { useResource } from "@/context/ResourceContext"


const LetterRecognitionProblemSet = () => {
    const {resource, setResource} = useResource();

    return(
        <h1>Letter Recognition Problem Set</h1>
    );
}

export default LetterRecognitionProblemSet;
