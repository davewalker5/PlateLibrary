# platelibrary

This project is a simple, SQLite-backed plate library for microscopy work, developed to support a set of ongoing personal microscopy investigations and the associated [Field Notes](https://davidwalker.uk) website.

It is is deliberately minimal, local-first, and practical and consists of a small set of tools that together provide a simple personal data system for recording plates, linking them to investigations, and exporting the data:

A typical workflow with the tool looks like this:

1.	Enter and edit plates via [Streamlit](https://streamlit.io)
2.	Explore and validate the data in [Datasette](https://datasette.io)
3.	Export the data to CSV
4.	Use the exported data in analysis / reports

## Getting Started

### Prerequisities

In order to run this image you'll need docker installed.

- [Windows](https://docs.docker.com/windows/started)
- [OS X](https://docs.docker.com/mac/started/)
- [Linux](https://docs.docker.com/linux/started/)

### Usage

#### Container Parameters

The following "docker run" parameters are recommended when running the platelibrary image:

| Parameter | Value                        | Purpose                                                              |
| --------- | ---------------------------- | -------------------------------------------------------------------- |
| -d        | -                            | Run as a background process                                          |
| -v        | /local:/var/opt/platelibrary | Mount the host folder containing the SQLite database and config file |
| -p        | 80:8501                      | Expose the container's port 8501 as port 80 on the host              |
| --rm      | -                            | Remove the container automatically when it stops                     |

For example:

```shell
docker run -d -v /local:/var/opt/platelibrary/ -p 80:8501 --rm davewalker5/platelibrary:latest
```

The "/local" path given to the -v argument is described, below, and should be replaced with a value appropriate for the host running the container. Similarly, the port number "80" can be replaced with any available port on the host.

### Volumes

The description of the container parameters, above, specifies that a folder containing the SQLite database file for the application is mounted in the running container, using the "-v" parameter.

That folder should contain a SQLite database named "plate_library.db", and a JSON-format configuration file containing these keys for centering and styling location maps, customised as necessary:

```json
{
    "location" : {
        "default_latitude": 51.75,
        "default_longitude": -1.25,
        "map_zoom": 11,
        "map_style": null,
        "attribution": null
    }
}
```

#### Running the Application

To run the image, enter the following commands, substituting "/local" for the host folder containing the SQLite database, as described:

```shell
docker run -d -v /local:/var/opt/platelibrary/ -p 80:8501 --rm davewalker5/platelibrary:latest
```

Once the container is running, browse to the following URL on the host:

http://localhost:80

You should see the plate maintenance entry page.

## Find Us

- [Plate Library on GitHub](https://github.com/davewalker5/PlateLibrary)

## Versioning

For the versions available, see the [tags on this repository](https://github.com/davewalker5/PlateLibrary/tags).

## Authors

- **Dave Walker** - _Initial work_ -

See also the list of [contributors](https://github.com/davewalker5/PlateLibrary/contributors) who
participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/davewalker5/PlateLibrary/blob/master/LICENSE) file for details.
