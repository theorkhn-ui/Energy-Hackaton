import { Config } from "@remotion/cli/config";

// Per storyboard tech spec: 1920x1080, 30 fps, H.264.
Config.setVideoImageFormat("jpeg");
Config.setCodec("h264");
Config.setOverwriteOutput(true);
