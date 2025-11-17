const InterviewPageLayout = ({children}) => {
  return (
    <div className='flex h-screen flex-col bg-linear-to-br from-dark to-black'>
      <div className='flex flex-1 overflow-hidden'>{children}</div>
    </div>
  );
};

export default InterviewPageLayout;
