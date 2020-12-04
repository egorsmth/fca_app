import React from 'react';
import ReactImageMagnify from 'react-image-magnify';
import Table from 'react-bootstrap/Table';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import Container from 'react-bootstrap/Container';


export default class Lattice extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      latticeImg: "",
      lattice: "",
      concept: "",
      openForm: false,
      formVals: {}
    };
    this.handleUploadFile = this.handleUploadFile.bind(this);
  }
  componentDidMount() {
    fetch('http://127.0.0.1:5000/')
    .then(async res => {
      let a = await res.json()
      return a
    }).then(data => {
      let dataI = data.latticeImg
      dataI = dataI.slice(2,-2)
      dataI = dataI.replace("b&#39;", "") //to get rid of start curly brace code 
      dataI = dataI.replace("&#39;", "")  //to get rid of end curly bracecode 
      dataI = `data:image/png;base64,${dataI}=`
      this.setState({
        formVals2: {json: ""},
        latticeImg: dataI,
        concept: data.concept,
        lattice: data.lattice,
        openForm: false,
        constructTime: data.constructTime,
        drawTime: data.drawTime,
        json: data.json,
        error: ""
      })
    });
  }

  openForm = () => {
    this.setState(
      {
        ...this.state,
        openForm: true
      }
    )
  }

  handleNameChange = (event) =>  {
    this.setState({
      ...this.state,
      formVals: {
        ...this.state.formVals,
        name: event.target.value
      }
    });
  }

  handleJsonChange = (event) => {
    this.setState({
      ...this.state,
      formVals2: {
        ...this.state.formVals2,
        json: event.target.value
      }
    });
  }

  handleAttrObjChange = (event) => {
    console.log(event.target.name)
    this.setState({
      ...this.state,
      formVals: {
        ...this.state.formVals,
        [event.target.name]: this.state.formVals[event.target.name] ? 0 : 1
      }
    });
  }

  handleUploadFile(ev) {
    ev.preventDefault();
    var self = this
    const data = new FormData();
    console.log(this.uploadInput)
    data.append('file', this.uploadInput.files[0]);

    fetch('http://127.0.0.1:5000/upload', {
      method: 'POST',
      body: data,
    })
    .then(async res => {
      if (!res.ok) {
        throw Error(res.statusText);
      }
      let a = await res.json()
      return a
    }).then(data => {
      let dataI = data.latticeImg
      dataI = dataI.slice(2,-2)
      dataI = dataI.replace("b&#39;", "") //to get rid of start curly brace code 
      dataI = dataI.replace("&#39;", "")  //to get rid of end curly bracecode 
      dataI = `data:image/png;base64,${dataI}=`
      this.setState({
        latticeImg: dataI,
        concept: data.concept,
        lattice: data.lattice,
        openForm: false,
        formVals: {},
        addTime: data.addTime,
        drawTime: data.drawTime,
        json: data.json,
        error: ""
      })
    })
    .catch(e => {
      self.setState({
        ...self.state,
        error: e + ""
      })
    });
  }

  submitAttribute = (event) => {
    console.log(this.state.formVals)
    event.preventDefault()

    fetch('http://127.0.0.1:5000/addattr', {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        old_concept: this.state.concept,
        old_lattice: this.state.lattice,
        attrM: this.state.formVals.name,
        attrMI: this.state.concept.G.map(x => this.state.formVals[x]? 1 : 0)
      })
    })
    .then(async res => {
      if (!res.ok) {
        throw Error(res.statusText);
      }
      let a = await res.json()
      return a
    }).then(data => {
      let dataI = data.latticeImg
      dataI = dataI.slice(2,-2)
      dataI = dataI.replace("b&#39;", "") //to get rid of start curly brace code 
      dataI = dataI.replace("&#39;", "")  //to get rid of end curly bracecode 
      dataI = `data:image/png;base64,${dataI}=`
      this.setState({
        latticeImg: dataI,
        concept: data.concept,
        lattice: data.lattice,
        openForm: false,
        formVals: {},
        addTime: data.addTime,
        drawTime: data.drawTime,
        json: data.json,
        error: ""
      })
    })
    .catch(e => {
      this.setState({
        ...this.state,
        error: e + ""
      })
    });
  }

  getFile = (e) => {
    e.preventDefault();
    const type = 'application/json'; // modify or get it from response
    const blob = new Blob([this.state.json], {type});

    // Step 2: Create Blob Object URL for that blob
    const url = URL.createObjectURL(blob);

    // Step 3: Trigger downloading the object using that URL
    const a = document.createElement('a');
    a.href = url;
    a.download = "out.json";
    a.click(); // triggering it manually
  };

  render() {
    if (this.state.latticeImg) {
      const head = [<td></td>]
      for (let index = 0; index < this.state.concept.M.length; index++) {
        head.push(<td key={index}>{this.state.concept.M[index]}</td>)
      }
      const body = []
      for (let objIdx = 0; objIdx < this.state.concept.G.length; objIdx++) {
        body.push([<td key={objIdx}>{this.state.concept.G[objIdx]}</td>])
        for (let Iidx = 0; Iidx < this.state.concept.M.length; Iidx++) {
          body[body.length - 1].push(<td>{this.state.concept.I[objIdx][Iidx] ? "X" : ""}</td>)
        }
      }

      let form = <Button onClick={this.state.openForm ? null : this.openForm}>
          Add attribute
        </Button>
      if (this.state.openForm) {
        form = <Form>
          <Form.Control 
            size="sm" type="text" placeholder="Attribute name" 
            value={this.state.formVals.name} onChange={this.handleNameChange}
          />
          <div key={`inline-checkbox`} className="mb-3">
            {this.state.concept.G.map((objName) => (
              <Form.Check
                name={objName} label={objName} type='checkbox' id={`inline-checkbox-${objName}`}
                onChange={this.handleAttrObjChange}  
              />
            ))}
          </div>
          <Button variant="primary" type="submit" onClick={this.state.openForm ? this.submitAttribute : null}>
            Add
          </Button>
        </Form>
      }
      let form2 = (<form onSubmit={this.handleUploadFile}>
                <br /><br />
        <div>
          <input ref={(ref) => { this.uploadInput = ref; }} type="file" />
        </div>
        <div>
        <Button variant="info"  type="submit" >Upload</Button>
        </div>
      </form>)
       
       let form3 = (<form onSubmit={this.getFile}>
          <br /><br />
        <div>
        <Button variant="success"  type="submit" >Download json</Button>
        </div>
      </form>)
      return <div>

        <Container fluid="lg">
          <ReactImageMagnify {...{
              smallImage: {
                alt: '',
                isFluidWidth: false,
                width: 600,
                height: 600,
                src: this.state.latticeImg,
            },
            largeImage: {
                src: this.state.latticeImg,
                width: 2000,
                height: 2000
            }
          }} />
          <div>
            {this.state.error ? <p style={{color:"red"}}> {this.state.error} </p> : ""}
            Create lattice time: {this.state.constructTime || "-"} sec<br></br>
            Add attribute time: {this.state.addTime || "-"} sec<br></br>
            Draw time: {this.state.drawTime || "-"} sec
          </div>
          <div>
            <Table striped bordered hover>
              <thead>
                <tr>
                  {head}
                </tr>
              </thead>
              <tbody>
                {body.map(x => <tr>{x}</tr>)}
              </tbody>
            </Table>
          </div>
          <div>
            {form}
          </div>
          <div>
            {form2}
          </div>
          <div>
            {form3}
          </div>
        </Container>

      </div>
    }
    return <div></div>
  }
}
