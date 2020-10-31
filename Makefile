help:
	@echo "clean - remove all artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove python artifacts"
	@echo "install - install the package"

clean: clean-build clean-pyc

clean-build:
	rm -rf build/
	rm -rf dist/
	rm -rf .eggs/
	find . -name '*.egg-info' -exec rm -rf {} +
	find . -name '*.egg' -exec rm -f {} +
	find . -name '.DS_Store' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +

dist:
	python3 -m pip install --user --upgrade setuptools wheel twine
	python3 setup.py sdist
	python3 setup.py bdist_wheel

release: dist
	@make dist
	python3 -m twine upload --repository pypi dist/*


install: clean
	python3 setup.py install