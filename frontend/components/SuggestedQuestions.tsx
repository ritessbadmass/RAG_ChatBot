'use client';

interface SuggestedQuestionsProps {
  onSelect: (question: string) => void;
}

const questions = [
  'What is the expense ratio of SBI Bluechip Fund?',
  'Minimum SIP amount for HDFC Flexi Cap?',
  'How can I download my capital gains statement?',
];

export default function SuggestedQuestions({ onSelect }: SuggestedQuestionsProps) {
  return (
    <div className="mb-8">
      <h3 className="text-sm font-medium text-gray-500 mb-3">Popular Questions</h3>
      <div className="flex flex-wrap gap-3">
        {questions.map((question, index) => (
          <button
            key={index}
            onClick={() => onSelect(question)}
            className="px-4 py-2 bg-white/80 hover:bg-white text-sm text-gray-700 rounded-lg border border-gray-200 hover:border-primary-300 transition-all shadow-sm"
          >
            {question}
          </button>
        ))}
      </div>
    </div>
  );
}
