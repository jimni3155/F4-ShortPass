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
      'rounded-full bg-black w-28 h-12 text-white font-semibold hover:bg-primary',
    secondary:
      'rounded-full bg-primary h-12 text-white font-semibold hover:bg-primary/90',
    ghost: 'text-sm text-primary border-none hover:text-primary/80',
    destructive: '',
    sucess: '',
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
