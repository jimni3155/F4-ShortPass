export default function Toggle({label, checked, onChange, description}) {
    return (
      <div className='flex items-start justify-between gap-4'>
        <div className='flex-1'>
          {label && <div className='text-sm font-medium text-text'>{label}</div>}
          {description && (
            <div className='text-sm text-gray-500 mt-1'>{description}</div>
          )}
        </div>
        <button
          type='button'
          role='switch'
          aria-checked={checked}
          onClick={() => onChange(!checked)}
          className={`relative inline-flex h-6 w-11 items-center rounded-full ${
            checked ? 'bg-black' : 'bg-gray-300'
          }`}>
          <span
            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
              checked ? 'translate-x-6' : 'translate-x-1'
            }`}
          />
        </button>
      </div>
    );
}
  