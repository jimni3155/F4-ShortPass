const Badge = ({children, classname = '', variant = 'ghost'}) => {
  const variants = {
    primary: 'bg-primary text-white rounded-full py-2 text-sm',
    ghost: 'text-black rounded-full py-2 text-sm',
    secondary: 'bg-blue text-white',
  };
  return (
    <div
      className={`${classname} ${variants[variant]} border-none text-center`}>
      {children}
    </div>
  );
};

export default Badge;
