import { useResource } from "@/context/ResourceContext"


const LetterWritingProblemSet = () => {
    const {resource, setResource} = useResource();

    return(
        <h1>Letter Writing Problem Set</h1>
    );
}

export default LetterWritingProblemSet;
