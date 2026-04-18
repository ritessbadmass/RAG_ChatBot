export default function KuveraHeader() {
  return (
    <header className="w-full bg-[var(--kuvera-surface)] border-b border-[var(--kuvera-border)] sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 lg:px-8 h-16 flex items-center justify-between">
        {/* Logo and Nav Links */}
        <div className="flex items-center gap-10">
          <div className="flex items-center gap-2 cursor-pointer">
            {/* Minimalist Kuvera-inspired geometric logo */}
            <svg className="w-8 h-8 text-[var(--kuvera-teal)]" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" opacity="0.8" />
            </svg>
            <span className="text-xl font-bold tracking-tight text-[var(--kuvera-navy)]">kuvera</span>
          </div>
          <nav className="hidden md:flex items-center gap-6 text-sm font-medium text-[var(--kuvera-text-muted)] mt-1">
            <a href="#" className="text-[var(--kuvera-teal)] border-b-2 border-[var(--kuvera-teal)] pb-5 mt-5">Mutual Funds</a>
            <a href="#" className="hover:text-[var(--kuvera-navy)] transition-colors pb-5 mt-5 border-b-2 border-transparent hover:border-[var(--kuvera-border)]">Stocks</a>
            <a href="#" className="hover:text-[var(--kuvera-navy)] transition-colors pb-5 mt-5 border-b-2 border-transparent hover:border-[var(--kuvera-border)]">US Stocks</a>
            <a href="#" className="hover:text-[var(--kuvera-navy)] transition-colors pb-5 mt-5 border-b-2 border-transparent hover:border-[var(--kuvera-border)]">Fixed Deposits</a>
          </nav>
        </div>

        {/* Right side actions */}
        <div className="flex items-center gap-6">
          <button className="hidden md:flex items-center gap-2 text-sm text-[var(--kuvera-text-muted)] hover:text-[var(--kuvera-navy)] transition-colors group">
            <svg className="w-5 h-5 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </button>
          <div className="flex items-center gap-3 cursor-pointer">
            <div className="w-9 h-9 rounded-full bg-[var(--kuvera-bg)] border border-[var(--kuvera-border)] text-[var(--kuvera-navy)] flex items-center justify-center text-sm font-semibold shadow-sm overflow-hidden">
              <svg className="w-5 h-5 text-[var(--kuvera-text-muted)] mt-1.5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M24 20.993V24H0v-2.996A14.977 14.977 0 0112.004 15c4.904 0 9.26 2.354 11.996 5.993zM16.002 8.999a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            </div>
            <svg className="w-4 h-4 text-[var(--kuvera-text-muted)] hidden sm:block" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>
      </div>
    </header>
  );
}
