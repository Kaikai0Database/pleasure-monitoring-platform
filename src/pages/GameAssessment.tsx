import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Footer } from '../components/Footer';
import { questions, EMOJI_OPTIONS, type Answer } from '../data/questions';
import { QuestionCard } from '../components/game/QuestionCard';
import { EmojiOption } from '../components/game/EmojiOption';

export const GameAssessment: React.FC = () => {
    const navigate = useNavigate();
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [answers, setAnswers] = useState<Answer[]>([]);
    const [isTransitioning, setIsTransitioning] = useState(false);

    const currentQuestion = questions[currentQuestionIndex];

    const handleAnswer = (emoji: string, score: number) => {
        if (isTransitioning) return;

        // Record the answer
        const newAnswer: Answer = {
            questionId: currentQuestion.id,
            emoji,
            score,
        };

        const newAnswers = [...answers, newAnswer];
        setAnswers(newAnswers);

        // Transition to next question or results
        setIsTransitioning(true);
        setTimeout(() => {
            if (currentQuestionIndex < questions.length - 1) {
                setCurrentQuestionIndex(currentQuestionIndex + 1);
                setIsTransitioning(false);
            } else {
                // Game complete, navigate to results
                navigate('/game/result', { state: { answers: newAnswers } });
            }
        }, 500);
    };

    return (
        <div
            className="fixed inset-0 flex flex-col items-center justify-center p-8 bg-cover bg-center transition-all duration-500"
            style={{ backgroundImage: currentQuestion.background }}
        >
            {/* Question Card */}
            <div className={`mb-12 transition-opacity duration-300 ${isTransitioning ? 'opacity-0' : 'opacity-100'}`}>
                <QuestionCard
                    questionNumber={currentQuestionIndex + 1}
                    totalQuestions={questions.length}
                    questionText={currentQuestion.text}
                />
            </div>

            {/* Emoji Options */}
            <div className={`flex flex-wrap justify-center gap-6 max-w-4xl transition-opacity duration-300 ${isTransitioning ? 'opacity-0' : 'opacity-100'}`}>
                {EMOJI_OPTIONS.map((option) => (
                    <EmojiOption
                        key={option.emoji}
                        emoji={option.emoji}
                        label={option.label}
                        onClick={() => handleAnswer(option.emoji, option.score)}
                    />
                ))}
            </div>

            {/* Hint text with background */}
            <div className="mt-8 inline-block bg-white bg-opacity-90 border-4 border-black px-6 py-3 shadow-[4px_4px_0_0_rgba(0,0,0,1)]">
                <p className="text-sm font-bold">請選擇最符合您感受的選項</p>
            </div>

            <div className="fixed bottom-0 w-full">
                <Footer />
            </div>
        </div>
    );
};
