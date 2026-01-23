import { useResource } from "@/context/ResourceContext"


const WordPronounciationProblemSet = () => {
    const {resource, setResource} = useResource();

    return(
        <h1>Word Pronounciation Problem Set</h1>
    );
}

export default WordPronounciationProblemSet;
