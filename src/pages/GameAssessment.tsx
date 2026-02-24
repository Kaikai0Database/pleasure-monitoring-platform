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
        <>
            <style>{`
                /* Assessment Layout Optimization */
                .assessment-container {
                    background-size: cover;
                    background-position: center bottom;
                    background-repeat: no-repeat;
                    background-attachment: scroll;
                    image-rendering: pixelated;
                    image-rendering: -moz-crisp-edges;
                    image-rendering: crisp-edges;
                }
                
                /* Responsive Grid - 2x2 to 1x4 on ultra-small screens */
                @media (max-width: 350px) {
                    .assessment-grid {
                        grid-template-columns: 1fr !important;
                    }
                }
            `}</style>
            <div
                className="flex flex-col assessment-container"
                style={{
                    backgroundImage: currentQuestion.background,
                    minHeight: '100dvh'
                }}
            >
                {/* Content Area - grows to push footer down */}
                <div
                    className="flex flex-col items-center p-4 sm:p-8"
                    style={{
                        flex: 1,
                        justifyContent: 'flex-start',
                        paddingBottom: '1rem',
                        width: '100%'
                    }}
                >
                    {/* Question Card */}
                    <div className={`mb-12 transition-opacity duration-300 ${isTransitioning ? 'opacity-0' : 'opacity-100'}`}>
                        <QuestionCard
                            questionNumber={currentQuestionIndex + 1}
                            totalQuestions={questions.length}
                            questionText={currentQuestion.text}
                        />
                    </div>

                    {/* Emoji Options - Responsive 2x2 Grid */}
                    <div
                        className={`transition-opacity duration-300 assessment-grid ${isTransitioning ? 'opacity-0' : 'opacity-100'}`}
                        style={{
                            display: 'grid',
                            gridTemplateColumns: 'repeat(2, 1fr)',
                            gap: '15px',
                            maxWidth: '500px',
                            width: '90%',
                            margin: '0 auto'
                        }}
                    >
                        {EMOJI_OPTIONS.map((option) => (
                            <EmojiOption
                                key={option.emoji}
                                emoji={option.emoji}
                                label={option.label}
                                onClick={() => handleAnswer(option.emoji, option.score)}
                            />
                        ))}
                    </div>
                </div>

                {/* Footer Section - Hint + Copyright */}
                <div
                    style={{
                        marginTop: 'auto',
                        paddingTop: '2rem',
                        paddingBottom: 'max(2rem, env(safe-area-inset-bottom))',
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        gap: '1rem',
                        width: '100%'
                    }}
                >
                    {/* Hint text with background */}
                    <div className="inline-block bg-white bg-opacity-90 border-4 border-black px-6 py-3 shadow-[4px_4px_0_0_rgba(0,0,0,1)]">
                        <p className="text-sm font-bold">請選擇最符合您感受的選項</p>
                    </div>

                    {/* Footer - Copyright */}
                    <Footer />
                </div>
            </div>
        </>
    );
};
