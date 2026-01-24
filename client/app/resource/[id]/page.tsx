import { useResource } from "@/context/ResourceContext";
import { PolymorphicResource } from "@/types/response_models/ResourceResponse";
import { useParams } from "next/navigation"
import { useEffect, useState } from "react";
import { ResourceType } from "@/types/enums";

// Import all resource page components
import InfoLecture from "@/app/info-lecture/page";
import LetterSpeakingLecture from "@/app/letter-speaking-lecture/page";
import LetterWritingLecture from "@/app/letter-writing-lecture/page";
import VocabLecture from "@/app/vocab-lecture/page";
import LetterPronounciationProblem from "@/app/letter-pronounciation-problem/page";
import WordPronounciationProblemSet from "@/app/word-pronounciation-problem-set/page";
import LetterRecognitionProblemSet from "@/app/letter-recognition-problem-set/page";
import LetterWritingProblemSet from "@/app/letter-writing-problem-set/page";
import VocabReadingProblemSets from "@/app/vocab-reading-problem-sets/page";
import VocabListeningProblemSets from "@/app/vocab-listening-problem-sets/page";
import VocabSpeakingProblemSets from "@/app/vocab-speaking-problem-sets/page";
import DialectSelection from "@/app/dialect-selection/page";
import DictationProblemSet from "@/app/dictation-problem-set/page";
import DiscriminationProblemSet from "@/app/discrimination-problem-set/page";
import LetterJoiningProblemSet from "@/app/letter-joining-problem-set/page";


const Resource = () => {
    const params = useParams();
    const resourceId = params.id;

    const {resource, setResource} = useResource();

    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string>("")

    useEffect(() => {
        const getResource = async () => {
            setIsLoading(true);
            const authToken = localStorage.getItem("token");

            try{
                const resourceResponse = await fetch(
                    `${process.env.NEXT_PUBLIC_SERVER_URL}/resource/${resourceId}`,
                    {
                        method: "GET",
                        headers: {
                        'Authorization': `Bearer ${authToken}`,
                        'Content-Type': 'application/json'
                        }
                    }
                );

                if(!resourceResponse.ok){
                    const errorData = await resourceResponse.json();
                    throw new Error(errorData.detail || "Error on fetching resource")
                }

                const resourceData = await resourceResponse.json();
                setResource({
                    ...resource!,
                    resource: resourceData
                });
            } catch(err){
                setError(err instanceof Error ? err.message : "Error in fetching resource data.");
            } finally{
                setIsLoading(false);
            }
        }

        getResource();
    }, [])

    // Render appropriate component based on resource type
    const renderResourcePage = () => {
        if (!resource?.resource) {
            return <div>Loading resource...</div>;
        }

        switch (resource.resource.resource_type) {
            case ResourceType.INFO_LECTURE:
                return <InfoLecture />;
            
            case ResourceType.LETTER_SPEAKING_LECTURE:
                return <LetterSpeakingLecture />;
            
            case ResourceType.LETTER_WRITING_LECTURE:
                return <LetterWritingLecture />;
            
            case ResourceType.VOCAB_LECTURE:
                return <VocabLecture />;
            
            case ResourceType.LETTER_PRONOUNCIATION_PROBLEM:
                return <LetterPronounciationProblem />;
            
            case ResourceType.WORD_PRONOUNCIATION_PROBLEM_SET:
                return <WordPronounciationProblemSet />;
            
            case ResourceType.LETTER_RECOGNITION_PROBLEM_SET:
                return <LetterRecognitionProblemSet />;
            
            case ResourceType.LETTER_WRITING_PROBLEM_SET:
                return <LetterWritingProblemSet />;
            
            case ResourceType.LETTER_JOINING_PROBLEM_SET:
                return <LetterJoiningProblemSet />;
            
            case ResourceType.VOCAB_READING_PROBLEM_SETS:
                return <VocabReadingProblemSets />;
            
            case ResourceType.VOCAB_LISTENING_PROBLEM_SETS:
                return <VocabListeningProblemSets />;
            
            case ResourceType.VOCAB_SPEAKING_PROBLEM_SETS:
                return <VocabSpeakingProblemSets />;
            
            case ResourceType.DIALECT_SELECTION:
                return <DialectSelection />;

            case ResourceType.DICTATION_PROBLEM_SET:
                return <DictationProblemSet />;

            case ResourceType.DISCRIMINATION_PROBLEM_SET:
                return <DiscriminationProblemSet />;
            
            default:
                return <div>Unknown resource type: {resource.resource.resource_type}</div>;
        }
    };

    return(
        <>
            {isLoading ? (
                <div>Loading...</div>
            ) : error ? (
                <div>Error: {error}</div>
            ) : (
                renderResourcePage()
            )}
        </>
    )
}

export default Resource;
