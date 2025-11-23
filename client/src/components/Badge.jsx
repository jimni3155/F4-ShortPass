const Badge = ({children, classname = '', variant = 'ghost'}) => {
  const variants = {
    primary: 'bg-primary text-white rounded-full py-2 text-sm',
    ghost: 'text-black rounded-lg py-1 text-sm',
    secondary:
      'px-2.5 py-1 rounded-lg bg-blue-50 text-blue-600 text-xs font-medium',
  };
  return (
    <div
      className={`${classname} ${variants[variant]} inline-flex items-center border-none text-center`}>
      {children}
    </div>
  );
};

export default Badge;
