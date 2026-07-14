using ECCD.Application.Cdcs.Queries;
using ECCD.Application.Common.Models;
using Microsoft.AspNetCore.Mvc;

namespace ECCD.API.Controllers;

public class CdcController : ApiControllerBase
{
    [HttpGet]
    public async Task<ActionResult<ApiResponse<List<CdcDto>>>> GetAll()
    {
        var result = await Mediator.Send(new GetCdcsQuery());
        if (!result.IsSuccess)
        {
            return BadRequest(ApiResponse<List<CdcDto>>.Fail("GET_CDCS_FAILED", result.Error ?? "Failed to load CDCs."));
        }
        return Ok(ApiResponse<List<CdcDto>>.Success(result.Data!));
    }
}
