{ pkgs }: {
  deps = [
    # Python and pip
    pkgs.python311
    pkgs.python311Packages.pip

    # PostgreSQL client libraries (required for psycopg2)
    pkgs.postgresql
    pkgs.postgresql.lib

    # Build tools for Python packages
    pkgs.gcc
    pkgs.gnumake
    pkgs.libffi
    pkgs.openssl
    pkgs.zlib

    # Rust and Cargo (for some Python packages that need compilation)
    pkgs.rustc
    pkgs.cargo
    pkgs.libiconv
    pkgs.libxcrypt

    # Node.js (if needed for any tooling)
    pkgs.nodejs_20
  ];

  env = {
    PYTHON_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      pkgs.postgresql.lib
      pkgs.openssl
      pkgs.libffi
      pkgs.zlib
    ];

    # PostgreSQL settings
    PGHOST = "localhost";
    PGPORT = "5432";
  };
}
