import upload from '@assets/svg/upload.svg';
import x from '@assets/svg/x.svg';

export default function PdfUpload({
  label,
  file,
  onFileChange,
  onRemove,
  required = false,
  error,
}) {
  const handleFileChange = (e) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      onFileChange(selectedFile);
    }
  };

  return (
    <div className='flex flex-col gap-2'>
      {label && (
        <label className='text-sm font-medium text-text'>
          {label}
          {required && <span className='text-red-500 ml-1'>*</span>}
        </label>
      )}

      {!file ? (
        <label
          className={`flex items-center justify-center gap-2 px-4 py-8 border-2 border-dashed rounded-lg cursor-pointer transition-colors ${
            error
              ? 'border-red-500'
              : 'border-gray-300 hover:border-primary hover:bg-[#8B5CF6]/5'
          }`}>
          <img className='w-5 h-5' src={upload} alt='파일 업로드' />
          <span className='text-sm text-grey'>
            PDF 파일을 선택하거나 드래그하세요
          </span>
          <input
            type='file'
            accept='.pdf'
            onChange={handleFileChange}
            className='hidden'
          />
        </label>
      ) : (
        <div className='flex items-center justify-between px-4 py-3 border border-gray-300 rounded-lg'>
          <span className='text-sm text-text'>{file.name}</span>
          <button
            type='button'
            onClick={onRemove}
            className='p-2 hover:bg-gray-200 rounded-lg transition-colors'>
            <img className='w-4 h-4' src={x} alt='취소' />
          </button>
        </div>
      )}

      {error && <span className='text-sm text-red-500'>{error}</span>}
    </div>
  );
}
