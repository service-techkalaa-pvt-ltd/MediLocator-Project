{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.tesseract
    pkgs.leptonica
    pkgs.zlib
    pkgs.libjpeg
    pkgs.libpng
    pkgs.grpc
    pkgs.glib
  ];
}
