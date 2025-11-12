const Select = ({
  label,
  value = '',
  options,
  onChange,
  placeholder = '선택해주세요',
  option = [],
  required = false,
  error,
  ...props
}) => {
  return (
    <div className='flex flex-col space-y-2'>
      {label && (
        <label className='text-sm font-medium text-text'>
          {label}
          {required && <span className='text-red-500 ml-1'>*</span>}
        </label>
      )}
      <select
        onChange={onChange}
        value={value}
        className={`px-4 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all ${
          error ? 'border-red-500' : 'border-gray-300'
        }`}
        placeholder='선택해주세요'>
        {options.map((option) => {
          return (
            <option className='bg-white' key={option.id} value={option.name}>
              {option.name}
            </option>
          );
        })}
      </select>
    </div>
  );
};

export default Select;
