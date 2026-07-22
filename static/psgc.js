document.addEventListener("DOMContentLoaded", function() {
    const regionSelect = document.getElementById('region');
    const provinceSelect = document.getElementById('province');
    const citySelect = document.getElementById('city');
    const barangaySelect = document.getElementById('barangay');
    const manualDiv = document.getElementById('manualAddressFields');
    const autoAddressArea = document.getElementById('auto_address');
    const isAutoInput = document.getElementById('is_auto_address');
    const btnAuto = document.getElementById('btnAutoLocation');

    if (!regionSelect) return; // In case this is loaded on a page without the form

    // Fetch Regions
    fetch('https://psgc.gitlab.io/api/regions/')
        .then(response => response.json())
        .then(data => {
            data.sort((a,b) => a.name.localeCompare(b.name));
            data.forEach(region => {
                const opt = document.createElement('option');
                opt.value = region.code;
                opt.textContent = region.name;
                opt.dataset.name = region.name;
                regionSelect.appendChild(opt);
            });
        });

    regionSelect.addEventListener('change', function() {
        const code = this.value;
        provinceSelect.innerHTML = '<option value="" disabled selected>Select Province</option>';
        citySelect.innerHTML = '<option value="" disabled selected>Select City/Town</option>';
        barangaySelect.innerHTML = '<option value="" disabled selected>Select Barangay</option>';
        provinceSelect.disabled = true;
        citySelect.disabled = true;
        barangaySelect.disabled = true;

        // Fetch Provinces for this region
        fetch(`https://psgc.gitlab.io/api/regions/${code}/provinces/`)
            .then(res => res.json())
            .then(provinces => {
                if(provinces.length > 0) {
                    provinces.sort((a,b) => a.name.localeCompare(b.name));
                    provinces.forEach(p => {
                        const opt = document.createElement('option');
                        opt.value = p.code;
                        opt.textContent = p.name;
                        opt.dataset.name = p.name;
                        provinceSelect.appendChild(opt);
                    });
                    provinceSelect.disabled = false;
                } else {
                    // NCR or independent cities might not have provinces under them in the API in the same way, 
                    // fetch cities directly for the region if no provinces
                    fetchCities(`https://psgc.gitlab.io/api/regions/${code}/cities-municipalities/`);
                }
            });
    });

    provinceSelect.addEventListener('change', function() {
        fetchCities(`https://psgc.gitlab.io/api/provinces/${this.value}/cities-municipalities/`);
    });

    function fetchCities(url) {
        citySelect.innerHTML = '<option value="" disabled selected>Select City/Town</option>';
        barangaySelect.innerHTML = '<option value="" disabled selected>Select Barangay</option>';
        barangaySelect.disabled = true;
        fetch(url)
            .then(res => res.json())
            .then(cities => {
                cities.sort((a,b) => a.name.localeCompare(b.name));
                cities.forEach(c => {
                    const opt = document.createElement('option');
                    opt.value = c.code;
                    opt.textContent = c.name;
                    opt.dataset.name = c.name;
                    citySelect.appendChild(opt);
                });
                citySelect.disabled = false;
            });
    }

    citySelect.addEventListener('change', function() {
        const code = this.value;
        barangaySelect.innerHTML = '<option value="" disabled selected>Select Barangay</option>';
        fetch(`https://psgc.gitlab.io/api/cities-municipalities/${code}/barangays/`)
            .then(res => res.json())
            .then(barangays => {
                barangays.sort((a,b) => a.name.localeCompare(b.name));
                barangays.forEach(b => {
                    const opt = document.createElement('option');
                    opt.value = b.code;
                    opt.textContent = b.name;
                    opt.dataset.name = b.name;
                    barangaySelect.appendChild(opt);
                });
                barangaySelect.disabled = false;
            });
            
        // Auto-fetch Zipcode
        if (window.isAutoFilling) return;
        const zipInput = document.getElementById('zipcode');
        if (zipInput && this.selectedIndex > 0) {
            let cityName = this.options[this.selectedIndex].text;
            let provName = "";
            if (provinceSelect && provinceSelect.selectedIndex > 0) {
                provName = provinceSelect.options[provinceSelect.selectedIndex].text;
            }
            
            // Clean up PSGC names for Nominatim
            cityName = cityName.replace(/CITY OF /ig, '').replace(/ CITY/ig, '').trim();
            provName = provName.replace(/PROVINCE OF /ig, '').replace(/\(.*\)/g, '').replace(/NATIONAL CAPITAL REGION/ig, 'Metro Manila').trim();
            
            const previousZip = zipInput.value;
            zipInput.value = "Fetching...";
            let query = cityName + (provName ? ", " + provName : "");
            
            fetch(`https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&country=Philippines&format=json&addressdetails=1`)
                .then(res => res.json())
                .then(data => {
                    let found = false;
                    for(let i=0; i<data.length; i++) {
                        if (data[i].address && data[i].address.postcode) {
                            zipInput.value = data[i].address.postcode;
                            found = true;
                            break;
                        }
                    }
                    if(!found && zipInput.value === "Fetching...") zipInput.value = previousZip;
                }).catch(() => {
                    if (zipInput.value === "Fetching...") zipInput.value = previousZip;
                });
        }
    });

    // Hidden inputs to store the text names instead of codes
    const form = regionSelect.closest('form');
    if (form) {
        form.addEventListener('submit', function() {
            if(isAutoInput.value === "0") {
                if(regionSelect.options[regionSelect.selectedIndex] && !regionSelect.options[regionSelect.selectedIndex].disabled) {
                    const rName = document.createElement('input');
                    rName.type = 'hidden'; rName.name = 'region_name'; rName.value = regionSelect.options[regionSelect.selectedIndex].text;
                    form.appendChild(rName);
                }
                if(!provinceSelect.disabled && provinceSelect.options[provinceSelect.selectedIndex] && !provinceSelect.options[provinceSelect.selectedIndex].disabled) {
                    const pName = document.createElement('input');
                    pName.type = 'hidden'; pName.name = 'province_name'; pName.value = provinceSelect.options[provinceSelect.selectedIndex].text;
                    form.appendChild(pName);
                }
                if(!citySelect.disabled && citySelect.options[citySelect.selectedIndex] && !citySelect.options[citySelect.selectedIndex].disabled) {
                    const cName = document.createElement('input');
                    cName.type = 'hidden'; cName.name = 'city_name'; cName.value = citySelect.options[citySelect.selectedIndex].text;
                    form.appendChild(cName);
                }
                if(!barangaySelect.disabled && barangaySelect.options[barangaySelect.selectedIndex] && !barangaySelect.options[barangaySelect.selectedIndex].disabled) {
                    const bName = document.createElement('input');
                    bName.type = 'hidden'; bName.name = 'barangay_name'; bName.value = barangaySelect.options[barangaySelect.selectedIndex].text;
                    form.appendChild(bName);
                }
            }
        });
    }

    // Geolocation API
    if (btnAuto) {
        btnAuto.addEventListener('click', function() {
            // Try to get location
            const originalBtnHtml = btnAuto.innerHTML;
            btnAuto.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Locating...';
            btnAuto.disabled = true;
            
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(function(position) {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;
                    fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`)
                        .then(res => res.json())
                        .then(async data => {
                            btnAuto.innerHTML = originalBtnHtml;
                            btnAuto.disabled = false;
                            
                            if (data && data.address) {
                                await autoFillAddress(data.address);
                            }
                        }).catch(err => {
                            alert("Failed to get address. Please select manually.");
                            btnAuto.innerHTML = originalBtnHtml;
                            btnAuto.disabled = false;
                        });
                }, function() {
                    alert("Location access denied or unavailable. Please select manually.");
                    btnAuto.innerHTML = originalBtnHtml;
                    btnAuto.disabled = false;
                });
            } else {
                alert("Geolocation is not supported by this browser.");
                btnAuto.innerHTML = originalBtnHtml;
                btnAuto.disabled = false;
            }
        });
    }

    async function autoFillAddress(addr) {
        window.isAutoFilling = true;
        // Match Region
        let matchedRegion = matchOption(regionSelect, [addr.region, addr.state, addr.state_district]);
        if (matchedRegion) {
            regionSelect.value = matchedRegion;
            regionSelect.dispatchEvent(new Event('change'));
            
            // Match Province
            await waitForOptions(provinceSelect, citySelect);
            if (!provinceSelect.disabled) {
                let matchedProv = matchOption(provinceSelect, [addr.state, addr.county, addr.province, addr.region]);
                if (matchedProv) {
                    provinceSelect.value = matchedProv;
                    provinceSelect.dispatchEvent(new Event('change'));
                }
            }
            
            // Match City
            await waitForOptions(citySelect, null);
            let matchedCity = matchOption(citySelect, [addr.city, addr.town, addr.municipality, addr.county]);
            if (matchedCity) {
                citySelect.value = matchedCity;
                citySelect.dispatchEvent(new Event('change'));
                
                // Match Barangay
                await waitForOptions(barangaySelect, null);
                let matchedBrgy = matchOption(barangaySelect, [addr.suburb, addr.village, addr.quarter, addr.neighbourhood, addr.residential]);
                if (matchedBrgy) {
                    barangaySelect.value = matchedBrgy;
                }
            }
        }
        
        // Zip code
        if (addr.postcode) {
            const zipInput = document.getElementById('zipcode');
            if(zipInput) zipInput.value = addr.postcode;
        }
        
        // House number & street
        let house = addr.house_number || '';
        let road = addr.road || '';
        const houseInput = document.getElementById('house_number');
        if(houseInput) houseInput.value = (house + " " + road).trim();
        
        window.isAutoFilling = false;
    }

    function matchOption(selectEl, possibleNames) {
        if(!possibleNames || possibleNames.length === 0) return null;
        let options = Array.from(selectEl.options);
        for (let name of possibleNames) {
            if (!name) continue;
            let cleanName = name.toLowerCase().replace(/city of|city|barangay|brgy\.?|province of/g, '').trim();
            for (let opt of options) {
                if (opt.disabled) continue;
                let optClean = opt.text.toLowerCase().replace(/city of|city|barangay|brgy\.?|province of/g, '').trim();
                if (optClean === cleanName || optClean.includes(cleanName) || cleanName.includes(optClean)) {
                    return opt.value;
                }
            }
        }
        return null;
    }

    function waitForOptions(selectEl, altSelectEl, timeout = 5000) {
        return new Promise(resolve => {
            let interval = setInterval(() => {
                if (selectEl.options.length > 1 || (altSelectEl && altSelectEl.options.length > 1)) {
                    clearInterval(interval);
                    resolve();
                }
            }, 200);
            setTimeout(() => { clearInterval(interval); resolve(); }, timeout);
        });
    }
});
