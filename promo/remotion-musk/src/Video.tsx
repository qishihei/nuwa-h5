import {
  AbsoluteFill, Sequence, Audio, staticFile,
  useCurrentFrame, spring, interpolate,
} from 'remotion';
import beats from './beats.json';

export const FPS = 30;
const BG = '#0e0e10', PANEL = '#16161a';
const BUB_YOU = '#2b6cff', BUB_MUSK = '#26262b';
const TXT = '#ebebee', DIM = '#96969e', ACCENT = '#e9c46a';
const FONT = "'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif";

const Msg = ({ m, last }: { m: any; last: boolean }) => {
  const frame = useCurrentFrame();
  const s = last ? spring({ frame, fps: FPS, config: { damping: 200 } }) : 1;
  const scale = last ? interpolate(s, [0, 1], [0.7, 1]) : 1;
  const op = last ? interpolate(s, [0, 1], [0, 1]) : 1;
  const isYou = m.speaker === 'you';
  return (
    <div style={{ marginBottom: 16, display: 'flex', flexDirection: 'column',
      alignItems: isYou ? 'flex-end' : 'flex-start' }}>
      {!isYou && <div style={{ color: DIM, fontSize: 26, marginBottom: 6 }}>埃隆·马斯克</div>}
      <div style={{ maxWidth: 700, backgroundColor: isYou ? BUB_YOU : BUB_MUSK,
        color: isYou ? '#ffffff' : TXT, padding: '18px 22px', borderRadius: 22,
        fontSize: 33, lineHeight: '46px', whiteSpace: 'pre-wrap',
        transform: `scale(${scale})`, opacity: op,
        transformOrigin: isYou ? 'bottom right' : 'bottom left' }}>
        {m.lines.join('\n')}
      </div>
    </div>
  );
};

const ChatScene = ({ messages, animateLast }: { messages: any[]; animateLast: boolean }) => (
  <AbsoluteFill style={{ backgroundColor: BG, fontFamily: FONT }}>
    <div style={{ position: 'absolute', top: 70, left: 40, right: 40, height: 130,
      borderRadius: 24, backgroundColor: PANEL, display: 'flex', flexDirection: 'column',
      justifyContent: 'center', padding: '0 32px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', color: TXT,
        fontSize: 40, fontWeight: 700 }}>
        <span>nuwa-h5 · 思想会客厅</span>
        <span style={{ color: ACCENT }}>埃隆·马斯克</span>
      </div>
      <div style={{ color: DIM, fontSize: 24, marginTop: 6 }}>
        AI 生成 · 灵感来自马斯克思维框架 · 非本人</div>
    </div>
    <div style={{ position: 'absolute', top: 240, left: 40, right: 40 }}>
      {messages.map((m, idx) => (
        <Msg key={idx} m={m} last={animateLast && idx === messages.length - 1} />
      ))}
    </div>
  </AbsoluteFill>
);

const CardScene = ({ text }: { text: string }) => (
  <AbsoluteFill style={{ backgroundColor: BG, fontFamily: FONT, display: 'flex',
    alignItems: 'center', justifyContent: 'center', padding: '0 80px' }}>
    <div style={{ color: TXT, fontSize: 58, lineHeight: '82px', textAlign: 'center',
      fontWeight: 700 }}>{text}</div>
  </AbsoluteFill>
);

const EndScene = ({ text }: { text: string }) => (
  <AbsoluteFill style={{ backgroundColor: BG, fontFamily: FONT, display: 'flex',
    flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
    <div style={{ color: TXT, fontSize: 50, lineHeight: '72px', textAlign: 'center',
      fontWeight: 700, padding: '0 80px', marginBottom: 60 }}>{text}</div>
    <img src={staticFile('qr.png')} style={{ width: 360, height: 360 }} />
    <div style={{ color: ACCENT, fontSize: 34, marginTop: 24 }}>扫码，把问题直接甩给马斯克</div>
    <div style={{ color: DIM, fontSize: 28, marginTop: 8 }}>nuwa-h5.onrender.com · 思想会客厅</div>
    <div style={{ color: DIM, fontSize: 24, marginTop: 24 }}>AI 生成演示，非真人言论，仅供娱乐</div>
  </AbsoluteFill>
);

export const ChatVideo = ({ beats }: { beats: any[] }) => {
  let cursor = 0;
  return (
    <AbsoluteFill style={{ backgroundColor: BG }}>
      {beats.map((b, i) => {
        const dur = Math.ceil((b.dur + 0.4) * FPS);
        const from = cursor; cursor += dur;
        return (
          <Sequence from={from} durationInFrames={dur} key={i}>
            {b.type === 'title' || b.type === 'cap'
              ? <CardScene text={b.text} />
              : b.type === 'end'
              ? <EndScene text={b.text} />
              : <ChatScene messages={b.messages} animateLast={true} />}
            <Audio src={staticFile(b.audio)} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
