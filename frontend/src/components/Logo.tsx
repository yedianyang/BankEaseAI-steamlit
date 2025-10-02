import React from 'react';
import { Banknote } from 'lucide-react';

interface LogoProps {
  onClick?: () => void;
  showText?: boolean;
  className?: string;
}

export default function Logo({ onClick, showText = true, className = '' }: LogoProps) {
  const handleClick = onClick || (() => {});
  const isClickable = !!onClick;

  return (
    <div
      onClick={handleClick}
      className={`flex items-center ${isClickable ? 'cursor-pointer group' : ''} ${className}`}
    >
      <Banknote className="h-8 w-8 text-primary-600" />
      {showText && (
        <h1 className={`ml-2 text-xl font-bold text-gray-900 ${isClickable ? 'group-hover:text-primary-600 transition-colors' : ''}`}>
          BankEase AI
        </h1>
      )}
    </div>
  );
}
