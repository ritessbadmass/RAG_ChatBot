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
    <div className="mb-8 px-2 mt-4">
      <h3 className="text-xs font-semibold mb-3 uppercase tracking-wider" style={{ color: 'var(--kuvera-text-muted)' }}>
        Suggested Questions
      </h3>
      <div className="flex flex-col gap-2.5">
        {questions.map((question, index) => (
          <button
            key={index}
            onClick={() => onSelect(question)}
            className="w-full text-left px-4 py-3 rounded-xl transition-all shadow-sm hover:shadow-md border"
            style={{ 
              background: 'var(--kuvera-surface)', 
              borderColor: 'var(--kuvera-border)',
              color: 'var(--kuvera-text)'
            }}
            onMouseEnter={e => (e.currentTarget.style.borderColor = 'var(--kuvera-teal)')}
            onMouseLeave={e => (e.currentTarget.style.borderColor = 'var(--kuvera-border)')}
          >
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">{question}</span>
              <svg className="w-4 h-4" style={{ color: 'var(--kuvera-teal)' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
