import {useState, useRef, useEffect} from 'react';
import down from '@assets/svg/chevron-down.svg';
import up from '@assets/svg/chevron-up.svg';

const Select = ({
  label,
  value,
  options,
  onChange,
  placeholder = '선택해주세요',
  required = false,
  error,
  ...props
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef(null);

  const selectedOption = options.find((option) => option.id === value);

  const handleOptionClick = (option) => {
    // 부모에서 onChange를 기존 select처럼 쓰고 있다면:
    // onChange?.({ target: { value: option.id, option } });
    onChange?.(option.id);
    setIsOpen(false);
  };

  return (
    <div className='flex flex-col space-y-2' ref={containerRef} {...props}>
      {label && (
        <label className='text-sm font-medium text-text'>
          {label}
          {required && <span className='text-red ml-1'>*</span>}
        </label>
      )}

      <div className='relative'>
        {/* Trigger */}
        <button
          type='button'
          onClick={() => setIsOpen((prev) => !prev)}
          className={`w-full px-4 py-3 flex items-center justify-between border rounded-lg bg-white text-sm transition-all
            ${error ? 'border-red' : 'border-gray-300 hover:border-gray-400'}
            focus:outline-none focus:ring-2 focus:ring-blue focus:border-transparent
          `}>
          <span
            className={`truncate ${
              selectedOption ? 'text-dark' : 'text-grey'
            }`}>
            {selectedOption ? selectedOption.name : placeholder}
          </span>
          {isOpen ? (
            <img className='w-4 h-4' src={up} alt='닫기' />
          ) : (
            <img className='w-4 h-4' src={down} alt='열기' />
          )}
        </button>

        {/* Options */}
        {isOpen && (
          <ul className='absolute z-20 mt-2 w-full max-h-56 overflow-y-auto rounded-lg border border-gray-200 bg-white shadow-lg text-sm'>
            {options.map((option) => {
              const isSelected = option.id === value;
              return (
                <li key={option.id}>
                  <button
                    type='button'
                    onClick={() => handleOptionClick(option)}
                    className={`w-full text-left px-4 py-2.5 transition-colors
                      ${
                        isSelected
                          ? 'bg-blue-50 text-blue'
                          : 'hover:bg-[#dae7f7] text-gray-800'
                      }
                    `}>
                    {option.name}
                  </button>
                </li>
              );
            })}
          </ul>
        )}
      </div>

      {error && <p className='text-xs text-red'>{error}</p>}
    </div>
  );
};

export default Select;
