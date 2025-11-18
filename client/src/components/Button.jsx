const Button = ({
  children,
  variant = 'primary',
  type = 'button',
  onClick,
  disabled = false,
  className = '',
}) => {
  const variants = {
    primary:
      'px-4 py-2 rounded-lg bg-blue text-white font-semibold hover:bg-blue/90',
    secondary:
      'rounded-full bg-primary h-12 text-white font-semibold hover:bg-primary/90',
    ghost: 'text-sm font-semibold border-none text-grey hover:text-dark',
    destructive: '',
    sucess: '',
    icon: 'rounded-full bg-primary hover:bg-primary/90 p-3',
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${className} ${variants[variant]} cursor-pointer`}>
      {children}
    </button>
  );
};

export default Button;
