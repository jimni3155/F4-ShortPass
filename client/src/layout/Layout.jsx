import {Outlet} from 'react-router-dom';

const Layout = () => {
  return (
    <div className='relative min-h-screen'>
      <div className='pointer-events-none fixed inset-0 -z-10'>
        <div
          className='absolute inset-0 opacity-60'
          style={{
            background:
              'radial-gradient(circle at top left, #dae7f7 0%, transparent 50%)',
          }}
        />
        {/* <div
          className='absolute inset-0 opacity-60'
          style={{
            background:
              'radial-gradient(circle at top right, #e2defc 0%, transparent 50%)',
          }}
        /> */}
        <div
          className='absolute inset-0'
          style={{
            background:
              'radial-gradient(circle at center, white 0%, transparent 70%)',
          }}
        />
      </div>
      {/* <header className='text-sm font-medium tracking-tight text-dark'>
        Flex AI
      </header> */}
      <div>
        <Outlet />
      </div>
    </div>
  );
};

export default Layout;
