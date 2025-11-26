import {Outlet} from 'react-router-dom';

const Layout = () => {
  return (
    <div className='relative min-h-screen'>
      <div>
        <Outlet />
      </div>
    </div>
  );
};

export default Layout;
