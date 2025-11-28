import upload from '@assets/svg/upload.svg';
import x from '@assets/svg/x.svg';

export default function PdfUpload({
  label,
  files = [],
  onFileChange,
  onRemove,
  required = false,
  error,
}) {
  const handleFileChange = (e) => {
    const selectedFile = e.target.files?.[0];

    // PDF 여부 체크
    if (selectedFile && selectedFile.type === 'application/pdf') {
      // 부모로 배열에 추가 요청
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

      {/* 업로드 드롭존 */}
      <label
        className={`flex items-center justify-center gap-2 px-4 py-15 border-2 border-dashed rounded-lg cursor-pointer transition-colors ${
          error
            ? 'border-red-500'
            : 'border-gray-300 hover:border-blue hover:bg-blue/5'
        }`}>
        <div className='flex-center flex-col gap-3'>
          <p className='text-sm text-grey flex-center gap-3'>
            <img className='w-5 h-5' src={upload} alt='파일 업로드' />
            PDF 파일을 선택하거나 드래그하세요
          </p>
          <p className='text-sm text-blue-600 hover:underline cursor-pointer'>
            파일 선택
          </p>
        </div>

        <input
          type='file'
          accept='.pdf'
          onChange={handleFileChange}
          className='hidden'
        />
      </label>

      {/* 업로드된 파일 리스트 */}
      {files.length > 0 && (
        <div className='mt-3 flex flex-col gap-2'>
          {files.map((file, index) => (
            <div
              key={index}
              className='flex items-center justify-between px-4 py-3 border border-gray-300 rounded-lg bg-white'>
              <span className='text-sm text-text'>{file.name}</span>

              <button
                type='button'
                onClick={() => onRemove(index)}
                className='p-2 hover:bg-gray-200 rounded-lg transition-colors'>
                <img className='w-4 h-4' src={x} alt='취소' />
              </button>
            </div>
          ))}
        </div>
      )}

      {error && <span className='text-sm text-red-500'>{error}</span>}
    </div>
  );
}
