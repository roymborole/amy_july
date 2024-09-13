import axios from 'axios';

export default async function handler(req, res) {
  const { path } = req.query;
  const url = `http://localhost:5000/${path.join('/')}`;

  try {
    const response = await axios({
      method: req.method,
      url: url,
      data: req.body,
      headers: req.headers,
    });

    res.status(response.status).json(response.data);
  } catch (error) {
    res.status(error.response?.status || 500).json(error.response?.data || { message: 'Internal Server Error' });
  }
}