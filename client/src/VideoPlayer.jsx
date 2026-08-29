export default function VideoPlayer(props) {
  return (
      <iframe
          style={{borderRadius: "15px"}}
      width="100%"
      height="400"
      src={`https://www.youtube.com/embed/${props.videoId}`}
      title="YouTube video player"
      allowFullScreen
    />
  );
}
