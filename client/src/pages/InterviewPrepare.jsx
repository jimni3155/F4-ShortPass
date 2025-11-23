import Button from '@components/Button';
import {useState, useRef, useEffect} from 'react';
import {useNavigate} from 'react-router-dom';
import Webcam from 'react-webcam';
import check_circle from '@assets/svg/check-circle.svg';
import alert_circle from '@assets/svg/alert-circle.svg';

const API_BASE = 'http://54.226.166.45:8000';

export default function InterviewPrepare() {
  const navigate = useNavigate();
  const videoRef = useRef(null);
  const [cameraReady, setCameraReady] = useState(false);
  const [micReady, setMicReady] = useState(false);
  const [isCheckingDevices, setIsCheckingDevices] = useState(true);
  const [cameraError, setCameraError] = useState(false);
  const [micError, setMicError] = useState(false);
  const [error, setError] = useState(null); // 에러 상태 추가
  const [loading, setLoading] = useState(false);

  // 목업 데이터
  const companyInfo = {
    companyName: '삼성물산 패션부문',
    jobTitle: '상품기획(MD) 신입',
    totalQuestions: 6,
    estimatedTime: '약 10분',
  };

  // 인터뷰 시작 요청
  useEffect(() => {
    const checkDevices = async () => {
      setIsCheckingDevices(true);

      try {
        // 카메라 체크
        const videoStream = await navigator.mediaDevices.getUserMedia({
          video: true,
        });
        if (videoRef.current) {
          videoRef.current.srcObject = videoStream;
        }
        setCameraReady(true);
        setCameraError(false);
      } catch (err) {
        console.error('Camera access error:', err);
        setCameraError(true);
      }

      try {
        // 마이크는 "권한만 요청"
        await navigator.mediaDevices.getUserMedia({audio: true});
        setMicReady(true);
        setMicError(false);
      } catch (err) {
        console.error('Microphone access error:', err);
        setMicError(true);
      }

      setIsCheckingDevices(false);
    };

    checkDevices();

    return () => {
      if (videoRef.current?.srcObject) {
        videoRef.current.srcObject.getTracks().forEach((t) => t.stop());
      }
    };
  }, []);

  const handleStartInterview = async () => {
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/api/v1/interviews/prepare`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          candidateId: '1',
          companyId: '1',
          personaInstanceIds: ['1', '2'],
        }),
      });

      const text = await res.text();
      console.log('prepare status:', res.status);
      console.log('prepare body:', text);

      if (!res.ok) {
        // 여기서 500 + 에러 메시지(detail)가 보일 거야
        return;
      }

      const data = JSON.parse(text);

      // 인터뷰 페이지로 이동하며 websocketUrl 전달
      navigate('/candidate/interview', {
        state: {
          websocketUrl: data.websocketUrl,
          interviewId: data.interviewId,
        },
      });
    } catch (err) {
      console.error('인터뷰 준비 실패', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGoBack = () => {
    navigate('/candidate/jobs');
  };

  const allDevicesReady = cameraReady && micReady && !isCheckingDevices;

  return (
    <div className='min-h-screen'>
      <div className='max-w-4xl mx-auto px-6 py-15'>
        {/* Header */}
        <div className='text-center mb-12'>
          <h1 className='text-3xl md:text-4xl font-bold text-blue mb-10'>
            면접을 시작하기 전에
          </h1>
          <p className='text-lg text-gray-600 mb-2'>
            <span className='font-semibold'>
              {companyInfo.companyName} / {companyInfo.jobTitle}
            </span>{' '}
            면접을 준비하고 있어요
          </p>
          <p className='text-base font-semibold text-gray-700'>
            원활한 진행을 위해 아래 항목들을 한 번만 점검해 주세요
          </p>
        </div>

        {/* 카메라 미리보기 */}
        <section className='mb-10'>
          <h2 className='text-base font-semibold text-dark mb-4'>
            웹캠 미리보기
          </h2>
          <div className='relative aspect-video bg-gray-900 rounded-2xl overflow-hidden shadow-lg'>
            <Webcam
              className='w-full h-full object-cover rounded-lg'
              audio={false}
              mirrored={true}
              videoConstraints={{
                width: 1280,
                height: 720,
                facingMode: 'user',
              }}
              muted
              playsInline
            />
            {!cameraReady && (
              <div className='absolute inset-0 flex items-center justify-center bg-gray-900'>
                <div className='text-center'>
                  {isCheckingDevices ? (
                    <p className='text-white text-lg'>카메라 연결 중...</p>
                  ) : cameraError ? (
                    <p className='text-white text-lg'>
                      카메라에 접근할 수 없습니다
                    </p>
                  ) : null}
                </div>
              </div>
            )}
          </div>
          <p className='text-sm text-gray-500 mt-3'>
            면접 중에는 화면이 녹화되지 않으며, 실시간 분석만 진행됩니다.
          </p>
        </section>

        {/* 장비 점검 */}
        <div>
          <h2 className='text-base font-semibold text-gray-900 mb-4'>
            카메라, 마이크, 오디오 상태를 확인해 주세요.
          </h2>
          <div className='border border-slate-200 rounded-xl p-6 mb-6'>
            {/* 카메라 상대 */}
            <div className='flex items-center gap-3 mb-4 pb-4 border-b border-slate-100'>
              <div className='p-2 rounded-lg'>
                {cameraReady && <img src={check_circle} className='w-5 h-5' />}
                {cameraError && <img src={alert_circle} className='w-5 h-5' />}
              </div>
              <div className='flex-1'>
                <p className='font-medium text-gray-900'>카메라</p>
                <p className='text-sm text-gray-500'>
                  {isCheckingDevices
                    ? '확인 중...'
                    : cameraReady
                    ? '정상 작동'
                    : '연결 실패'}
                </p>
              </div>
            </div>

            {/* 마이크 상태 */}
            <div className='flex items-center gap-3 mb-4 pb-4 border-b border-slate-100'>
              <div className='p-2 rounded-lg'>
                {micReady && <img src={check_circle} className='w-5 h-5' />}
                {micError && <img src={alert_circle} className='w-5 h-5' />}
              </div>
              <div className='flex-1'>
                <p className='font-medium text-gray-900'>마이크</p>
                <p className='text-sm text-gray-500'>
                  {isCheckingDevices
                    ? '확인 중...'
                    : micReady
                    ? '정상 작동'
                    : '연결 실패'}
                </p>
              </div>
            </div>

            {/* 스피커 */}
            <div className='flex items-center gap-3'>
              <div className='p-2 rounded-lg'>
                <img src={check_circle} className='w-5 h-5' />
              </div>
              <div className='flex-1'>
                <p className='font-medium text-gray-900'>스피커</p>
                <p className='text-sm text-gray-500'>질문을 들을 수 있습니다</p>
              </div>
            </div>
          </div>
        </div>
        {/* Tips Section */}
        <div className=' border border-slate-200 rounded-xl p-6 mb-8'>
          <h3 className='font-semibold text-gray-900 mb-3'>면접 팁</h3>
          <ul className='space-y-2 text-sm text-gray-700'>
            <li>- 조용한 환경에서 면접을 진행해 주세요</li>
            <li>- 인터넷 연결이 안정적인지 확인해 주세요</li>
            <li>- 카메라를 정면으로 바라보며 답변해 주세요</li>
            <li>
              - 면접 도중 나가기를 누르면 진행 상황이 저장되지 않을 수 있습니다
            </li>
          </ul>
        </div>

        {/* Action Buttons */}
        <div className='flex justify-between items-center'>
          <Button variant='ghost' onClick={handleGoBack}>
            이전
          </Button>
          <Button
            variant='primary'
            onClick={handleStartInterview}
            disabled={!allDevicesReady}
            className='disabled:opacity-50 disabled:cursor-not-allowed'>
            {isCheckingDevices ? (
              <span className='flex items-center gap-2'>
                {/* <Loader2 className='w-5 h-5 animate-spin' /> */}
                준비 중...
              </span>
            ) : (
              '면접 시작하기'
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
