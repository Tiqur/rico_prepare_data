{
  inputs = {
    # nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    systems.url = "github:nix-systems/default";
  };

  outputs = { systems, nixpkgs, ... } @ inputs: let
    eachSystem = f: nixpkgs.lib.genAttrs (import systems) (system: f nixpkgs.legacyPackages.${system});
  in {
    #packages = eachSystem (pkgs: {
    #  hello = pkgs.hello;
    #});

    devShells = eachSystem (pkgs: {
      default = pkgs.mkShell {
        buildInputs = with pkgs; [
          python310Packages.python
        ];

        shellHook = ''
          export LD_LIBRARY_PATH=${pkgs.lib.makeLibraryPath [
          ]}

          export QT_PLUGIN_PATH=venv/lib/python3.10/site-packages/PyQt5/Qt5/plugins

          # Create a virtual environment if not already created
          if [ ! -d ".venv" ]; then
            python3 -m venv .venv
          fi

          # Activate the virtual environment
          source .venv/bin/activate

          # Install non-Nix packages using pip
          pip install --upgrade pip
        '';
      };
    });
  };
}
