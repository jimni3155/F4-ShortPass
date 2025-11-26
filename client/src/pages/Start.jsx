import hero from '@assets/images/hero.png';
import Button from '@components/Button';
import {useNavigate} from 'react-router-dom';
import check_circle from '@assets/svg/check-circle-white.svg';
import zap from '@assets/svg/zap.svg';
import eye from '@assets/svg/eye.svg';

export default function HomePage() {
  const navigate = useNavigate();
  return (
    <div className='relative min-h-screen'>
      {/* 헤더 */}
      <header className='border-b border-gray-100 px-6 py-8 lg:px-12'>
        <div className='mx-auto flex max-w-7xl items-center justify-between'>
          <div className='text-2xl font-bold tracking-tight text-blue'>
            SHORT-PASS
          </div>
        </div>
      </header>

      <main>
        {/* Hero 섹션 */}
        <section className='px-8 py-16 lg:px-12 lg:py-24 md:mb-10'>
          <div className='mx-auto max-w-7xl text-center'>
            {/* 제목 */}
            <h1 className='mb-10 text-5xl font-semibold leading-tight tracking-tight text-grey lg:text-7xl'>
              기업을 위한 HR 스크리닝 서비스,
              <br />
              <span className='text-blue'>SHORT-PASS</span>
            </h1>

            {/* 설명 */}
            <p className='mx-auto mb-12 max-w-2xl text-lg leading-relaxed text-gray-600 lg:text-xl'>
              SHORT-PASS는 AI 면접과 데이터 분석으로 기업과 지원자의
              <br />
              완벽한 매칭을 지원하는 채용 어시스턴트 플랫폼입니다.
            </p>

            {/* 버튼 */}
            <div className='mb-18 flex items-center justify-center gap-8'>
              <Button
                variant='primary'
                className='h-12 rounded-full text-lg font-medium'
                onClick={() => navigate('/company/info')}>
                채용하고 싶어요
              </Button>

              <Button
                variant='outline'
                className='h-12 rounded-full text-lg font-medium'
                onClick={() => navigate('/candidate/info')}>
                지원하고 싶어요
              </Button>
            </div>

            <div className='relative mx-auto max-w-6xl'>
              {/* 그라데이션 */}
              <div className='absolute inset-0 -z-10 translate-y-1/4 bg-linear-to-br from-blue-400 via-blue-300 to-purple-300 opacity-80 blur-3xl' />

              {/* Snippet */}
              <div className='relative overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-2xl'>
                <img src={hero} className='w-full' />
              </div>
            </div>
          </div>
        </section>

        {/* 기능 소개 */}
        <section className='bg-linear-to-b from-gray-800 to-gray-900 px-6 py-20 lg:px-12 lg:py-32'>
          <div className='mx-auto max-w-7xl'>
            <div className='grid grid-cols-1 gap-12 lg:grid-cols-3'>
              {/* 소개 1 */}
              <div className='text-center'>
                <div className='mb-6 flex justify-center'>
                  <div className='flex h-12 w-12 items-center justify-center rounded-full bg-white/10'>
                    <img src={check_circle} className='h-6 w-6' />
                  </div>
                </div>
                <h3 className='mb-4 text-2xl font-bold text-white'>
                  빠른 면접 진행
                </h3>
                <p className='text-base leading-relaxed text-blue-100'>
                  AI가 자동으로 면접을 진행하고 즉시 결과를 제공합니다.
                  <br />
                  시간과 비용을 대폭 절감하세요.
                </p>
              </div>

              {/* 소개 2 */}
              <div className='text-center'>
                <div className='mb-6 flex justify-center'>
                  <div className='flex h-12 w-12 items-center justify-center rounded-full bg-white/10'>
                    <img src={eye} className='h-6 w-6' />
                  </div>
                </div>
                <h3 className='mb-4 text-2xl font-bold text-white'>
                  정확한 역량 평가
                </h3>
                <p className='text-base leading-relaxed text-blue-100'>
                  직무별 핵심 역량을 기준으로 지원자를 평가하고
                  <br />
                  데이터 기반의 객관적인 인사이트를 제공합니다.
                </p>
              </div>

              {/* 소개 3 */}
              <div className='text-center'>
                <div className='mb-6 flex justify-center'>
                  <div className='flex h-12 w-12 items-center justify-center rounded-full bg-white/10'>
                    <img src={zap} className='h-6 w-6' />
                  </div>
                </div>
                <h3 className='mb-4 text-2xl font-bold text-white'>
                  자동화된 리포트
                </h3>
                <p className='text-base leading-relaxed text-blue-100'>
                  면접 기록부터 평가 요약까지 자동으로 생성되어
                  <br />
                  채용 의사결정을 효율적으로 지원합니다.
                </p>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
