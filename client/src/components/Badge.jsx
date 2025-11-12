const Badge = ({children, classname = '', variant = 'ghost'}) => {
  const variants = {
    primary: 'bg-primary text-white',
    ghost: 'text-black',
  };
  return (
    <div
      className={`${classname} ${variants[variant]} rounded-full border-none text-center text-sm py-2`}>
      {children}
    </div>
  );
};

export default Badge;
